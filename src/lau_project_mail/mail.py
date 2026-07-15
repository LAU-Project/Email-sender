import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ollama import chat

from .exceptions import MissingFieldError, GenerationError, SendError

class Mail:
    def __init__(self, prompt: str, model: str) -> None:
        self.prompt = prompt
        self.model = model
        self.message = MIMEMultipart()

        self.context = None

        self.sender = None
        self.recipient = None
        self.subject = None
        self.body = None
        self.password = None

    def set_recipient(self, recipient: str, debug=False) -> None:
        if not recipient:
            raise ValueError("recipient must be a non-empty string")
        self.recipient = recipient
        self.message["To"] = self.recipient
        if debug:
            print(f"set_recipient: The recipient of the mail is set to {self.recipient}")

    def set_sender(self, sender: str, password: str, debug=False) -> None:
        if not sender or not password:
            raise ValueError("sender and password must be non-empty strings")
        self.sender = sender
        self.password = password
        self.message["From"] = self.sender
        if debug:
            print(f"set_sender: The sender of the mail is set to {self.sender}")

    def set_context(self, context: str, mail_subject: str, debug=False) -> None:
        if not context:
            raise ValueError("context must be a non-empty string")
        self.context = context
        self.mail_suject = mail_subject
        if debug:
            print(f"set_context: The subject context of the mail is set to {self.mail_suject}")
            print(f"set_context: The context of the mail is set to {self.context}")

    def generate(self, debug=False) -> None:
        if self.context is None:
            raise MissingFieldError("no context given, use set_context method")
        if self.recipient is None:
            raise MissingFieldError("no recipient given, use set_recipient method")
        if self.sender is None:
            raise MissingFieldError("no sender given, use set_sender method")

        try:
            stream = chat(
                model=self.model,
                messages=[{"role": "user", "content": self.prompt + self.context}],
            )
        except Exception as e:
            raise GenerationError(f"LLM call failed: {e}") from e

        response = stream.message.content
        if not response or not response.strip():
            raise GenerationError("LLM returned an empty response")
        response = response.strip()

        lines = response.splitlines()
        generated_subject = ""
        generated_body_lines = []

        in_body = False
        for line in lines:
            if line.lower().startswith("objet :"):
                generated_subject = line.split(":", 1)[1].strip()
                continue
            if generated_subject and line.strip() == "":
                in_body = True
                continue
            if in_body:
                generated_body_lines.append(line)

        body = "\n".join(generated_body_lines).strip()

        if not generated_subject:
            raise GenerationError("could not parse a subject ('Objet :') from the LLM response")
        if not body:
            raise GenerationError("could not parse a body from the LLM response")

        self.set_body(body, debug)
        self.set_subject(generated_subject, debug)
        self.message.attach(MIMEText(self.body, "plain"))

    def set_subject(self, subject: str, debug=False) -> None:
        if not subject:
            raise ValueError("subject must be a non-empty string")
        self.message["Subject"] = subject
        self.subject = subject
        if debug:
            print(f"set_subject: The subject of the mail is set to {self.subject}")

    def set_body(self, body: str, debug=False) -> None:
        if not body:
            raise ValueError("body must be a non-empty string")
        self.body = body
        if debug:
            print(f"set_body: The body of the mail is set to {self.body}")

    def send(self) -> None:
        if self.body is None:
            raise MissingFieldError("you need to use the generate method before")

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
                serveur.login(self.sender, self.password)
                serveur.sendmail(self.sender, self.recipient, self.message.as_string())
        except smtplib.SMTPAuthenticationError as e:
            raise SendError(f"authentication failed for {self.sender}: {e}") from e
        except smtplib.SMTPException as e:
            raise SendError(f"SMTP error while sending to {self.recipient}: {e}") from e
        except OSError as e:
            raise SendError(f"network error while connecting to SMTP server: {e}") from e

        print("Email envoyé.")

    def preview(self) -> None:
        if self.context is None:
            raise MissingFieldError("no context given, use set_context method")
        if self.recipient is None:
            raise MissingFieldError("no recipient given, use set_recipient method")
        if self.sender is None:
            raise MissingFieldError("no sender given, use set_sender method")
        if self.body is None:
            raise MissingFieldError("no body generated, use generate method")
        print(f"From: {self.sender}")
        print(f"To: {self.recipient}")
        print(f"Subject: {self.subject}")
        print(self.body)