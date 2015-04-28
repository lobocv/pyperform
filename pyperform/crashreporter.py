__author__ = 'calvin'

import logging
import traceback
import os

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


class CrashReporter(object):

    def __init__(self, username, password, recipients, mailserver):
        self.user = username
        self.pw = password
        self.recipients = recipients
        self.mailserver = mailserver

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
            msg['Subject'] = self.subject()

            # Add the body of the message as HTML
            html_body = self.body(etype, evalue, tb)
            msg.attach(MIMEText(html_body, 'html'))

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

    def subject(self):
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


