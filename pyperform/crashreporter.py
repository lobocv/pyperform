__author__ = 'calvin'

import logging
import traceback
import os

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
    :param mailserver: smtplib.SMTP object
    '''

    def __init__(self, username, password, recipients, mailserver, html=False):
        self.user = username
        self.pw = password
        self.recipients = recipients
        self.mailserver = mailserver
        self.html = html

    def __enter__(self):
        logging.info('CrashReporter: Enabled')

    def __exit__(self, etype, evalue, tb):
        if etype:
            logging.info('CrashReporter: Crash detected!')

            msg = MIMEMultipart()
            if isinstance(self.recipients, list) or isinstance(self.recipients, tuple):
                msg['To'] = ', '.join(self.recipients)
            else:
                msg['To'] = self.recipients
            msg['From'] = self.user
            msg['Subject'] = self.subject(etype, evalue, tb)

            # Add the body of the message
            body = self.body(etype, evalue, tb)
            if self.html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body))

            # Add any attachments
            attachments = self.attachments()
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(attachments, 'rb').read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                'attachment; filename="%s"' % os.path.basename(attachment))
                msg.attach(part)

            ms = self.mailserver
            ms.ehlo()
            ms.starttls()
            ms.ehlo()
            ms.login(self.user, self.pw)
            ms.sendmail(self.user, self.recipients, msg.as_string())
            ms.close()
        else:
            logging.info('CrashReporter: No crashes detected.')
            logging.info('CrashReporter: Exiting.')

    def subject(self, etype, evalue, tb):
        return 'Crash Report'

    def body(self, etype, evalue, tb):
        body = '\n'.join(traceback.format_exception(etype, evalue, tb))
        return body

    def attachments(self):
        """
        Generate and return a list of attachments to send with the report.
        :return: List of strings containing the paths to the files.
        """
        return []


