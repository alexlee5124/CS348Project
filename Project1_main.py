from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Sequence, MetaData, BIGINT, delete, update, ForeignKeyConstraint, DateTime, Index
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import inspect
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from datetime import datetime

INSTANCE_CONNECTION_NAME = f"cs348project-407715:us-central1:cs348project"
DB_USER = "user"
DB_PASS = "user1234"
DB_NAME = "project"

# initialize Connector object
connector = Connector()

print(sys.version)

# function to return the database connection object
def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pymysql",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn
engine = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)
connection = engine.connect()
Base = declarative_base()
Session = sqlalchemy.orm.sessionmaker(expire_on_commit = True)
Session.configure(bind=engine)
session = Session()

"""
inspector = inspect(engine)

for table_name in inspector.get_table_names():
   print(table_name)


connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS Purchase"))
connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS Card"))
connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS Account"))
connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS User"))
session.commit()
"""

class User(Base):
    __tablename__ = "User"
    username = Column(String(length=50), primary_key = True, index=True)
    password = Column(String(length=50))
    __table_args__ = (Index('user_username_idx', "username"), {})

    def __repr__(self):
        return "<User(username='{0}', password='{1}')>".format(
                            self.username, self.password)

    def create_new_user(self, session):
        session.add(self)
        session.commit()
    
    def delete_user(self, session, connection):
        session.delete(self)
        session.commit()

    def update_user(self, newUsername, newPassword):
        session.query(User).filter_by(username=self.username).update({'username':newUsername,'password':newPassword})
        session.commit()

class Account(Base):
    __tablename__ = "Account"
    accountNumber = Column(Integer, primary_key = True)
    routingNumber = Column(Integer, primary_key = True)
    username = Column(String(length=50), ForeignKey(User.username, ondelete='CASCADE',onupdate='CASCADE'), nullable=False)
    name = Column(String(length=50))
    amount = Column(Integer)

    def __repr__(self):
        return "<Account(accountNumber='{0}', routingNumber='{1}', name='{2}', amount ='{3}')>".format(
                            self.accountNumber, self.routingNumber, self.name, self.amount)
    
    def create_new_account(self, session):
        session.add(self)
        session.commit()

    def delete_account(self, session):
        account = session.get(Account, (self.accountNumber, self.routingNumber))
        session.delete(account)
        session.commit()
    
    def update_amount(self, amount, session):
        self.amount += amount
        session.commit()
    
    def update_name(self, newName, session):
        self.name = newName
        session.commit()

class Card(Base):
    __tablename__ = "Card"
    cardNumber = Column(BIGINT, primary_key = True)
    security = Column(Integer)
    accountNumber = Column(Integer, nullable=False)
    routingNumber = Column(Integer, nullable=False)
    __table_args__ = (ForeignKeyConstraint([accountNumber, routingNumber], [Account.accountNumber, Account.routingNumber],ondelete="CASCADE"), {})

    def add_new_card(self, session):
        session.add(self)
        session.commit()
    
    def delete_card(self, session):
        card = session.get(Card, self.cardNumber)
        session.delete(card)
        session.commit()

class Purchase(Base):
    __tablename__ = "Purchase"
    purchaseID = Column(Integer, Sequence('purchaseID'), primary_key = True)
    username = Column(String(length=50), ForeignKey(User.username, ondelete = 'CASCADE', onupdate='CASCADE'), nullable=False)
    accountNumber = Column(Integer, nullable=False)
    routingNumber = Column(Integer, nullable=False)
    cardNumber = Column(BIGINT, ForeignKey(Card.cardNumber), nullable=False)
    amount = Column(Integer)
    purchaseDate = Column(DateTime, default=datetime.now(), index=True)
    __table_args__ = (ForeignKeyConstraint([accountNumber, routingNumber], [Account.accountNumber, Account.routingNumber]), Index('purchase_date_idx', "purchaseDate"), {})

    def add_new_purchase(self, session, account):
        session.add(self)
        account.update_amount(-self.amount, session)
        session.commit()


Base.metadata.create_all(engine)

account = None
user = None

def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    session.close()
    sys.exit(app.exec_())

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initialize()

    def initialize(self):

        login_button = QPushButton('Log In', self)
        login_button.clicked.connect(self.login)

        signup_button = QPushButton('Sign Up', self)
        signup_button.clicked.connect(self.signup)


        vbox = QVBoxLayout()
        vbox.addWidget(login_button)
        vbox.addWidget(signup_button)
        self.setLayout(vbox)

        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Personal Budgeter')
        self.show()

    def login(self):
        self.login_window = LoginPage()
        self.close()

    def signup(self):
        self.signup_window = SignupPage()
        self.close()

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        self.initialize()

    def initialize(self):
        label_username = QLabel('Username:')
        self.username_entry = QLineEdit(self)

        label_password = QLabel('Password:')
        self.password_entry = QLineEdit(self)

        login_button = QPushButton('Log In', self)
        login_button.clicked.connect(self.login)

        goback_button = QPushButton('Go Back', self)
        goback_button.clicked.connect(self.goback)

        vbox = QVBoxLayout()
        vbox.addWidget(label_username)
        vbox.addWidget(self.username_entry)
        vbox.addWidget(label_password)
        vbox.addWidget(self.password_entry)
        vbox.addWidget(login_button)
        vbox.addWidget(goback_button)

        self.setLayout(vbox)

        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Log In')
        self.show()

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()

        global user
        user = session.query(User).filter_by(username=username, password=password).all()
        if len(user) == 0:
            print("USER DOESN'T EXIST")
            self.mainWindow = MainWindow()
            self.close()
        else:
            user = user[0]
            print(user)
            self.mainPage = MainPage()
            self.close()

        print(f'Logging in with username: {username}, password: {password}')

    def goback(self):
        self.mainWindow = MainWindow()
        self.close()

class SignupPage(QWidget):
    def __init__(self):
        super().__init__()

        self.initialize()

    def initialize(self):
        label_username = QLabel('Username:')
        self.username_entry = QLineEdit(self)

        label_password = QLabel('Password:')
        self.password_entry = QLineEdit(self)

        signup_button = QPushButton('Sign Up', self)
        signup_button.clicked.connect(self.signup)

        goback_button = QPushButton('Go Back', self)
        goback_button.clicked.connect(self.goback)

        vbox = QVBoxLayout()
        vbox.addWidget(label_username)
        vbox.addWidget(self.username_entry)
        vbox.addWidget(label_password)
        vbox.addWidget(self.password_entry)
        vbox.addWidget(signup_button)
        vbox.addWidget(goback_button)

        self.setLayout(vbox)

        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Sign Up')
        self.show()

    def signup(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        global user
        user = User(username=username, password=password)
        user.create_new_user(session)
        session.commit()

        self.mainPage = MainPage()
        self.close()

        print(f'Signing up with username: {username}, password: {password}')

    def goback(self):
        self.mainWindow = MainWindow()
        self.close()

class MainPage(QWidget):
    def __init__(self):
        super().__init__()

        self.initialize()

    def initialize(self):
        add_account_button = QPushButton('Add New Bank Account', self)
        add_account_button.clicked.connect(self.show_add_account_page)

        add_card_button = QPushButton('Add New Card', self)
        add_card_button.clicked.connect(self.show_add_card_page)

        add_purchase_button = QPushButton('Add New Purchase', self)
        add_purchase_button.clicked.connect(self.show_add_purchase_page)

        view_report_button = QPushButton('View Report', self)
        view_report_button.clicked.connect(self.show_view_report_page)

        update_user_button = QPushButton('Update User', self)
        update_user_button.clicked.connect(self.show_update_user_page)

        delete_user_button = QPushButton('Delete User', self)
        delete_user_button.clicked.connect(self.show_delete_user_page)

        logout_button = QPushButton('Log Out', self)
        logout_button.clicked.connect(self.logout)

        vbox = QVBoxLayout()
        vbox.addWidget(add_account_button)
        vbox.addWidget(add_card_button)
        vbox.addWidget(add_purchase_button)
        vbox.addWidget(view_report_button)
        vbox.addWidget(update_user_button)
        vbox.addWidget(delete_user_button)
        vbox.addWidget(logout_button)

        self.setLayout(vbox)

        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Main Page')
        self.show()

    def show_add_account_page(self):
        self.add_account_page = AddAccountPage()
        self.close()

    def show_add_card_page(self):
        self.add_card_page = AddCardPage()
        self.close()

    def show_add_purchase_page(self):
        self.add_purchase_page = AddPurchasePage()
        self.close()

    def show_view_report_page(self):
        self.view_report_page = ViewReportPage()
        self.close()

    def show_update_user_page(self):
        self.update_user_page = UpdateUserPage()
        self.close()

    def show_delete_user_page(self):
        user.delete_user(session, connection)
        print(user)
        print("User Deleted")
        self.mainWindow = MainWindow()
        self.close()

    def logout(self):
        global user
        user = None
        self.mainWindow = MainWindow()
        self.close()

class AddAccountPage(QWidget):
    def __init__(self):
        super().__init__()

        self.initialize()
    
    def initialize(self):
            account_label = QLabel('Account Number:')
            self.account_input = QLineEdit()

            routing_label = QLabel('Routing Number:')
            self.routing_input = QLineEdit()

            name_label = QLabel('Account Name:')
            self.name_input = QLineEdit()

            amount_label = QLabel('Amount:')
            self.amount_input = QLineEdit()

            create_button = QPushButton('Create')
            create_button.clicked.connect(self.create_account)

            goback_button = QPushButton('Go Back', self)
            goback_button.clicked.connect(self.goback)

            layout = QVBoxLayout()
            layout.addWidget(account_label)
            layout.addWidget(self.account_input)
            layout.addWidget(routing_label)
            layout.addWidget(self.routing_input)
            layout.addWidget(name_label)
            layout.addWidget(self.name_input)
            layout.addWidget(amount_label)
            layout.addWidget(self.amount_input)
            layout.addWidget(create_button)
            layout.addWidget(goback_button)

            self.setGeometry(100, 100, 400, 400)
            self.setLayout(layout)
            self.setWindowTitle('Add Account')
            self.show()

    def create_account(self):
        accountNumber = self.account_input.text()
        routingNumber = self.routing_input.text()
        amount = self.amount_input.text()
        accountName = self.name_input.text()

        print(f"Account Number: {accountNumber}, Routing Number: {routingNumber}, Account Name: {accountName}")
        global account
        account = Account(accountNumber = int(accountNumber), routingNumber=int(routingNumber), username=user.username, name=accountName, amount=int(amount))
        account.create_new_account(session)

        self.mainPage = MainPage()
        self.close()

    def goback(self):
        self.mainPage = MainPage()
        self.close()

class AddCardPage(QWidget):
    def __init__(self):
        super().__init__()

        self.initialize()

    def initialize(self):

        card_label = QLabel('Enter Card Number:')
        self.card_input = QLineEdit()

        security_label = QLabel('Enter Security Number:')
        self.security_input = QLineEdit()

        bankAccounts = session.query(Account).filter_by(username=user.username).all()

        account_label = QLabel('Select Account Number:')
        self.account_combo = QComboBox()
        self.account_combo.addItems([f"Account Number:{account.accountNumber}" for account in bankAccounts])

        routing_label = QLabel('Select Routing Number:')
        self.routing_combo = QComboBox()
        self.routing_combo.addItems([f"Routing number:{account.routingNumber}" for account in bankAccounts])

        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.submit_card)

        goback_button = QPushButton('Go Back', self)
        goback_button.clicked.connect(self.goback)

        layout = QVBoxLayout()
        layout.addWidget(card_label)
        layout.addWidget(self.card_input)
        layout.addWidget(security_label)
        layout.addWidget(self.security_input)
        layout.addWidget(account_label)
        layout.addWidget(self.account_combo)
        layout.addWidget(routing_label)
        layout.addWidget(self.routing_combo)
        layout.addWidget(submit_button)
        layout.addWidget(goback_button)

        self.setGeometry(100, 100, 400, 400)
        self.setLayout(layout)
        self.setWindowTitle('Add Card')

        self.show()

    def submit_card(self):
        cardNumber = self.card_input.text()
        security = self.security_input.text()
        selected_account = self.account_combo.currentText()
        selected_routing = self.routing_combo.currentText()
        accountNumber = selected_account.split(':')[1][:]
        routingNumber = selected_routing.split(':')[1][:]

        print(accountNumber)
        print(routingNumber)

        card = Card(cardNumber=cardNumber,security=security,accountNumber=int(accountNumber),routingNumber=int(routingNumber))
        card.add_new_card(session)

        self.mainPage = MainPage()
        self.close()

    def goback(self):
        self.mainPage = MainPage()
        self.close()

class AddPurchasePage(QWidget):
    def __init__(self):
        super().__init__()

        self.initialize()

    def initialize(self):
        global user
        bankAccounts = session.query(Account).filter_by(username=user.username).all()
        bank_label = QLabel('Select Bank Account:')
        self.bank_combo = QComboBox()
        self.bank_combo.addItems([f"Name:{account.name} | Account Number:{account.accountNumber} | Routing number:{account.routingNumber}" for account in bankAccounts])
        self.bank_combo.currentIndexChanged.connect(self.populate_card)

        self.card_label = QLabel('Select Card Number:')
        self.card_combo = QComboBox()
        self.populate_card()

        self.amount_label = QLabel('Enter Amount:')
        self.amount_input = QLineEdit()

        self.label = QLabel('Date:')
        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)


        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.submit_purchase)

        goback_button = QPushButton('Go Back', self)
        goback_button.clicked.connect(self.goback)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(bank_label)
        layout.addWidget(self.bank_combo)
        layout.addWidget(self.card_label)
        layout.addWidget(self.card_combo)
        layout.addWidget(self.amount_label)
        layout.addWidget(self.amount_input)
        layout.addWidget(submit_button)
        layout.addWidget(goback_button)
        layout.addWidget(self.date_input)


        self.setGeometry(100, 100, 400, 400)
        self.setLayout(layout)
        self.setWindowTitle('Add Purchase')
        self.show()
    
    def populate_card(self):
        self.card_combo.clear()

        bankInfo = self.bank_combo.currentText()
        bankInfos = bankInfo.split('|')
        bankRouting = bankInfos[2].split(':')[1][:]
        bankAccount = bankInfos[1].split(':')[1][:]

        cardNumbers = session.query(Card).filter_by(accountNumber=int(bankAccount), routingNumber=int(bankRouting)).all()
        self.card_combo.addItems([f"Number:{card.cardNumber}" for card in cardNumbers])


    def submit_purchase(self):
        bankInfo = self.bank_combo.currentText() 
        bankInfos = bankInfo.split('|')
        bankRouting = bankInfos[2].split(':')[1][:]
        bankAccount = bankInfos[1].split(':')[1][:]
        cardInfo = self.card_combo.currentText() 
        cardNumber = cardInfo.split(':')[1][:]
        amount = self.amount_input.text()
        date = self.date_input.date().toPyDate()

        global user
        global account
        account = session.query(Account).filter_by(accountNumber=bankAccount, routingNumber=bankRouting).all()[0]
        purchase = Purchase(username=user.username, accountNumber=int(bankAccount), routingNumber=int(bankRouting), cardNumber=int(cardNumber), amount=int(amount), purchaseDate=date)
        purchase.add_new_purchase(session, account)
        print(f"Bank Account: {bankAccount}, Card: {cardNumber}, Amount: {amount}")

        self.mainPage = MainPage()
        self.close()

    def goback(self):
        self.mainPage = MainPage()
        self.close()


class ViewReportPage(QWidget):
    def __init__(self):
        super().__init__()

        self.initialize()

    def initialize(self):
        start_date_label = QLabel('Start Date:')
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)

        end_date_label = QLabel('End Date:')
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)

        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.generate_report)

        goback_button = QPushButton('Go Back', self)
        goback_button.clicked.connect(self.goback)

        layout = QVBoxLayout()
        layout.addWidget(start_date_label)
        layout.addWidget(self.start_date_input)
        layout.addWidget(end_date_label)
        layout.addWidget(self.end_date_input)
        layout.addWidget(submit_button)
        layout.addWidget(goback_button)

        self.setGeometry(100, 100, 400, 400)
        self.setLayout(layout)
        self.setWindowTitle('View Report Page')

        self.show()

    def generate_report(self):
        start_date = self.start_date_input.date().toPyDate()
        end_date = self.end_date_input.date().toPyDate()

        report_data = f"Report from {start_date} to {end_date}"
        print(report_data)

        report_window = ReportWindow(start_date,end_date)
        report_window.exec_()

        self.MainPage=MainPage()
        self.close()

    def goback(self):
        self.mainPage = MainPage()
        self.close()

class ReportWindow(QDialog):
    def __init__(self, startDate, endDate):
        super().__init__()

        self.setWindowTitle('Purchases')

        total = 0

        global user
        purchases = session.query(Purchase).filter(Purchase.purchaseDate >= startDate,
                                                 Purchase.purchaseDate <= endDate, Purchase.username==user.username).order_by(Purchase.username, Purchase.purchaseDate).all()

        report_layout = QVBoxLayout()
        # Create widgets for the report window
        for purchase in purchases:
            total += purchase.amount
            purchaseLabel = QLabel(f"Date:{purchase.purchaseDate} | Amount:{purchase.amount}")
            report_layout.addWidget(purchaseLabel)

        totalPurchaseLabel = QLabel(f"Total Purchase Amount:{total}")
        report_layout.addWidget(totalPurchaseLabel)

        accounts = session.query(Account).filter(Account.username==user.username).order_by(Account.routingNumber, Account.accountNumber).all()
        for account in accounts:
            accountLabel = QLabel(f"Routing Number:{account.routingNumber} | Account Number:{account.accountNumber} | Current Balance:{account.amount}")
            report_layout.addWidget(accountLabel)


        self.setLayout(report_layout)
        self.show()

class UpdateUserPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initialize()
    
    def initialize(self):
        username_label = QLabel('New Username:')
        self.username_input = QLineEdit()

        password_label = QLabel('New Password:')
        self.password_input = QLineEdit()

        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.update_user)

        goback_button = QPushButton('Go Back', self)
        goback_button.clicked.connect(self.goback)

        layout = QVBoxLayout()
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(submit_button)
        layout.addWidget(goback_button)


        self.setGeometry(100, 100, 400, 400)
        self.setLayout(layout)
        self.setWindowTitle('Update User Page')
        self.show()

    def update_user(self):
        newUsername = self.username_input.text()
        newPassword = self.password_input.text()

        global user
        user.update_user(newUsername=newUsername, newPassword=newPassword)

        self.mainPage = MainPage()
        self.close()

    def goback(self):
        self.mainPage = MainPage()
        self.close()

if __name__ == '__main__':
    main()