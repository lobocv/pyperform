__author__ = 'calvin'

import traceback
import os
import glob
import datetime
import shutil
import smtplib
import time
import logging

from threading import Thread
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

class CrashReporter(object):
    '''
    Create a context manager that emails a report with the traceback on a crash.
    :param username: sender's email account
    :param password: sender's email account password
    :param recipients: list of report recipients
    :param smtp_host: smtp host address for smtplib.SMTP object
    :param smtp_port: smtp port for smtplib.SMTP object
    :param html: Use HTML message for email (True) or plain text (False).
    '''

    def __init__(self, username, password, recipients, smtp_host, smtp_port=0, html=False, report_dir=None,
                 check_interval=5*60, logger=None, offline_report_limit=5):
        self.user = username
        self.pw = password
        self.recipients = recipients
        self.html = html
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self._enabled = True
        self.logger = logger if logger else logging.getLogger(__name__)
        # Setup the directory used to store offline crash reports
        self.report_dir = report_dir
        self.check_interval = check_interval
        self._offline_report_limit = offline_report_limit
        self._watcher = None
        self._watcher_enabled = False
        if report_dir:
            if os.path.exists(report_dir):
                self.start_watcher()
            else:
                os.makedirs(report_dir)

    def enable(self):
        self.logger.info('CrashReporter: Enabled')
        self._enabled = True

    def disable(self):
        self.logger.info('CrashReporter: Disabled')
        self._enabled = False
        self.stop_watcher()

    def start_watcher(self):
        if self._get_offline_reports():
            self.logger.info('CrashReporter: Starting watcher.')
            self._watcher = Thread(target=self._watcher_thread, name='offline_reporter')
            self._watcher.setDaemon(True)
            self._watcher_enabled = True
            self._watcher.start()

    def stop_watcher(self):
        """
        Stop the watcher thread that tries to send offline reports.
        """
        if self._watcher:
            self._watcher_enabled = False
            self.logger.info('CrashReporter: Stopping watcher.')

    def __enter__(self):
        self.enable()

    def __exit__(self, etype, evalue, tb):
        if self._enabled:
            self.logger.exception('CrashReporter: Crash detected!')
            if etype:
                self._etype = etype
                self._evalue = evalue
                self._tb = tb
                great_success = self._sendmail(self.subject(), self.body(), self.attachments(), html=self.html)
                if not great_success:
                    self._save_report()
        else:
            self.logger.info('CrashReporter: No crashes detected.')

    def subject(self):
        return 'Crash Report'

    def body(self):
        body = datetime.datetime.now().strftime('%d %B %Y, %I:%M %p\n')
        body += '\n'.join(traceback.format_exception(self._etype, self._evalue, self._tb))
        return body

    def attachments(self):
        """
        Generate and return a list of attachments to send with the report.
        :return: List of strings containing the paths to the files.
        """
        return []

    def _sendmail(self, subject, body, attachments=None, html=False):
        msg = MIMEMultipart()
        if isinstance(self.recipients, list) or isinstance(self.recipients, tuple):
            msg['To'] = ', '.join(self.recipients)
        else:
            msg['To'] = self.recipients
        msg['From'] = self.user
        msg['Subject'] = subject

        # Add the body of the message
        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body))

        # Add any attachments
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(attachments, 'rb').read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                'attachment; filename="%s"' % os.path.basename(attachment))
                msg.attach(part)

        try:
            ms = smtplib.SMTP(self.smtp_host, self.smtp_port)
            ms.ehlo()
            ms.starttls()
            ms.ehlo()
            ms.login(self.user, self.pw)
            ms.sendmail(self.user, self.recipients, msg.as_string())
            ms.close()
        except Exception as e:
            self.logger.error('CrashReporter: %s' % e)
            return False

        return True

    def _save_report(self):
        """
        Save the crash report to a file. Keeping the last 5 files in a cyclical FIFO buffer.
        The newest crash report is 01
        """
        offline_reports = self._get_offline_reports()
        if offline_reports:
            # Increment the name of all existing reports
            for ii, report in enumerate(reversed(offline_reports)):
                n = int(report[-2:])
                new_name = os.path.join(self.report_dir, "crashreport%02d" % (n + 1))
                shutil.copy2(report, new_name)
            os.remove(report)
            # Delete the oldest report
            if len(offline_reports) >= self._offline_report_limit:
                oldest = os.path.join(self.report_dir, "crashreport%02d" % (self._offline_report_limit + 1))
                os.remove(oldest)

        # Write a new report
        report_path = os.path.join(self.report_dir, "crashreport01")
        with open(report_path, 'w') as _f:
            _f.write(self.body())

    def _send_offline_reports(self):
        offline_reports = self._get_offline_reports()
        if offline_reports:
            # Add the body of the message
            body = 'Here is a list of crash reports that were stored offline.\n'
            body += '-------------------------------------------------\n'
            for report in offline_reports:
                with open(report, 'r') as _f:
                    text = _f.readlines()
                    body += ''.join(text)
                    body += '-------------------------------------------------\n'
            great_success = self._sendmail(self.subject(), body)
            if great_success:
                for report in offline_reports:
                    os.remove(report)
                self.logger.info('CrashReporter: Offline reports sent.')
            return great_success

    def _get_offline_reports(self):
        return sorted(glob.glob(os.path.join(self.report_dir, "crashreport*")))

    def _watcher_thread(self):
        great_success = False
        while not great_success:
            time.sleep(self.check_interval)
            if not self._watcher_enabled:
                break
            self.logger.info('CrashReporter: Attempting to send offline reports.')
            great_success = self._send_offline_reports()
        self.logger.info('CrashReporter: Watcher stopped.')