import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ollama import chat

class Mail:
    def __init__(self, prompt:str, model:str) -> None:
        """
        INPUT: 
        - prompt: the prompt for the llm
        - model: the llm model to use
        \n
        OUTPUT:
        - None
        \n
        The constructor of the Mail class. This class generate and send mail with a llm.
        """
        self.prompt = prompt
        self.model = model
        self.message = MIMEMultipart()
        
        self.context = None
    
        self.sender = None
        self.recipient = None
        self.subject = None
        self.body = None

    def set_recipient(self, recipient:str, debug=False) -> None:
        """
        INPUT:
        - recipient: the email to sent the mail
        - debug: default to False, if true the method will display some text
        \n
        OUTPUT:
        - None
        \n
        This method will set the recipient of the mail.
        """
        self.recipient = recipient
        self.message["To"] = self.recipient
        if (debug is True):
            print(f"set_recipient: The recipient of the mail is set to {self.recipient}")

    def set_sender(self, sender:str, password:str, debug=False) -> None:
        """
        INPUT:
        - sender: the email to connect and send the mail (have to be a gmail for the moment)
        - password: the password for application for this email
        - debug: default to False, if true the method will display some text
        \n
        OUTPUT:
        - None
        \n
        This method will set the senderof the mail and it's password.
        """
        self.sender = sender
        self.password = password
        self.message["From"] = self.sender
        if (debug is True):
            print(f"set_sender: The sender of the mail is set to {self.sender}")

    def set_context(self, context:str, mail_subject:str, debug=False) -> None:
        """
        INPUT:
        - context: the context use for generating the complete mail
        - mail_subject: the possible subject of the mail
        - debug: default to False, if true the method will display some text
        \n
        OUTPUT:
        - None
        \n
        This method will set the context and a mail subject use for the generation of the mail.
        """
        self.context = context
        self.mail_suject = mail_subject
        if (debug is True):
            print(f"set_context: The subject context of the mail is set to {self.mail_suject}")
            print(f"set_context: The context of the mail is set to {self.context}")

    def generate(self, debug=False) -> None:
        """
        INPUT:
        - debug: default to False, if true the method will display some text
        \n
        OUTPUT:
        - None
        \n
        This method will generate the mail with the previously given informations.
        """
        if (self.context is None):
            print("generate: no context given, use set_context method")
            return
        if (self.recipient is None):
            print("generate: no recipient given, use set_recipient method")
            return
        if (self.sender is None):
            print("generate: no sender given, use set_sender method")
            return

        stream = chat(
            model=self.model,
            messages=[{"role":"user", "content":self.prompt + self.context}],
        )
        response = stream.message.content.strip()

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

        self.set_body("\n".join(generated_body_lines).strip(), debug)
        self.set_subject(generated_subject, debug)
        self.message.attach(MIMEText(self.body, "plain"))

    def set_subject(self, subject:str, debug=False) -> None:
        """
        INPUT:
        - subject: the subject to set for the mail
        - debug: default to False, if true the method will display some text
        \n
        OUTPUT:
        - None
        \n
        This method will set the subject of the mail.
        """
        self.message["Subject"] = subject
        self.subject = subject
        if (debug is True):
            print(f"set_body: The body of the mail is set to {self.subject}")
    
    def set_body(self, body:str, debug=False) -> None:
        """
        INPUT:
        - body: the body to set for the mail
        - debug: default to False, if true the method will display some text
        \n
        OUTPUT:
        - None
        \n
        This method will set the body of the mail.
        """
        self.body = body
        if (debug is True):
            print(f"set_body: The body of the mail is set to {self.body}")

    def send(self) -> None:
        """
        INPUT:
        - None
        \n
        OUTPUT:
        - None
        \n
        This method will send the mail.
        """
        if (self.body is None):
            print("send: you need to use the generate method before")
            return
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
            serveur.login(self.sender, self.password)
            serveur.sendmail(self.sender, self.recipient, self.message.as_string())
            print("Email envoyé.")

    def preview(self) -> None:
        """
        INPUT:
        - None
        \n
        OUTPUT:
        - None
        \n
        This method give you a preview of the mail.
        """
        if (self.context is None):
            print("preview: no context given, use set_context method")
            return
        if (self.recipient is None):
            print("preview: no recipient given, use set_recipient method")
            return
        if (self.sender is None):
            print("preview: no sender given, use set_sender method")
            return
        if (self.body is None):
            print("preview: no body generated, use generate method")
            return
        print(f"From: {self.sender}")
        print(f"To: {self.recipient}")
        print(f"Subject: {self.subject}")
        print(self.body)

