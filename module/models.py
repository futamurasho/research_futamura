from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# --- 1. モデル定義 ---
Base = declarative_base()

#団体情報
class Organization(Base):
    __tablename__ = 'organization'
    id             = Column(Integer, primary_key=True)
    name           = Column(String(200), nullable=False)
    year           = Column(String(10))
    representative = Column(String(100))
    accountant     = Column(String(100))
    submitted_date = Column(Date)

    income_summary = relationship("IncomeSummary", uselist=False, back_populates="organization")
    loans          = relationship("Loan", back_populates="organization")
    other_incomes  = relationship("OtherIncome", back_populates="organization")
    expense_summary = relationship("ExpenseSummary", uselist=False, back_populates="organization")
    routine_expenses = relationship("RoutineExpense", uselist=False, back_populates="organization")
    political_activity = relationship("PoliticalActivityExpense", uselist=False, back_populates="organization")
    donors         = relationship("Donor", back_populates="organization")

#収支
class IncomeSummary(Base):
    __tablename__ = 'income_summary'
    org_id               = Column(Integer, ForeignKey('organization.id'), primary_key=True)
    total_amount         = Column(Integer, default=0)
    membership_fee       = Column(Integer, default=0)
    personal_donation    = Column(Integer, default=0)
    corporate_donation   = Column(Integer, default=0)
    political_org_donation = Column(Integer, default=0)

    organization = relationship("Organization", back_populates="income_summary")

#借入金
class Loan(Base):
    __tablename__ = 'loans'
    id      = Column(Integer, primary_key=True, autoincrement=True)
    org_id  = Column(Integer, ForeignKey('organization.id'), nullable=False)
    lender  = Column(String(200), nullable=False)
    amount  = Column(Integer, nullable=False)
    date    = Column(Date, nullable=False)

    organization = relationship("Organization", back_populates="loans")

#その他の収入
class OtherIncome(Base):
    __tablename__ = 'other_incomes'
    id      = Column(Integer, primary_key=True, autoincrement=True)
    org_id  = Column(Integer, ForeignKey('organization.id'), nullable=False)
    item    = Column(String(200))
    amount  = Column(Integer)
    source  = Column(String(200))
    date    = Column(Date)

    organization = relationship("Organization", back_populates="other_incomes")

#支出
class ExpenseSummary(Base):
    __tablename__ = 'expense_summary'
    org_id       = Column(Integer, ForeignKey('organization.id'), primary_key=True)
    total_amount = Column(Integer, default=0)

    organization = relationship("Organization", back_populates="expense_summary")

#経常経費
class RoutineExpense(Base):
    __tablename__ = 'routine_expenses'
    org_id       = Column(Integer, ForeignKey('organization.id'), primary_key=True)
    total_amount = Column(Integer, default=0)
    personnel    = Column(Integer, default=0)
    utilities    = Column(Integer, default=0)
    supplies     = Column(Integer, default=0)
    office_rent  = Column(Integer, default=0)

    organization = relationship("Organization", back_populates="routine_expenses")

#政治活動費の親テーブル
class PoliticalActivityExpense(Base):
    __tablename__ = 'political_activity_expense'
    id           = Column(Integer, primary_key=True, autoincrement=True)
    org_id       = Column(Integer, ForeignKey('organization.id'), nullable=False)
    total_amount = Column(Integer, default=0)
    created_at   = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="political_activity")
    details      = relationship("PoliticalActivityExpenseDetail", back_populates="parent")

#政治活動費の明細テーブル
class PoliticalActivityExpenseDetail(Base):
    __tablename__ = 'political_activity_expense_detail'
    id                          = Column(Integer, primary_key=True, autoincrement=True)
    political_activity_expense_id = Column(Integer, ForeignKey('political_activity_expense.id'), nullable=False)
    minor_category              = Column(String(50), nullable=False)
    purpose                     = Column(String(200))
    amount                      = Column(Integer, nullable=False)
    date                        = Column(Date, nullable=False)
    payee                       = Column(String(200))
    location                    = Column(String(200))

    parent = relationship("PoliticalActivityExpense", back_populates="details")

#寄付者一覧
class Donor(Base):
    __tablename__ = 'donors'
    id      = Column(Integer, primary_key=True, autoincrement=True)
    org_id  = Column(Integer, ForeignKey('organization.id'), nullable=False)
    name    = Column(String(100))
    amount  = Column(Integer, nullable=False)
    address = Column(String(255))
    date    = Column(Date, nullable=False)

    organization = relationship("Organization", back_populates="donors")