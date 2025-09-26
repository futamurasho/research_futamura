import json
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Date, DateTime,
    ForeignKey, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker



# --- 3. JSON 読み込み & INSERT ---
def load_and_insert(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    session = Session()
    try:
        # 1) organization
        org_info = data["団体情報"]
        org = Organization(
            name=org_info["団体名"],
            year=org_info["年度"],
            representative=org_info["代表者"],
            accountant=org_info["会計責任者"],
            submitted_date=datetime.strptime(org_info["提出日"], "%Y-%m-%d").date() if org_info["提出日"] else None
        )
        session.add(org)
        session.flush()  # org.id を取得するため

        # 2) income_summary
        inc = data["収入"]
        income_sum = IncomeSummary(
            org_id=org.id,
            total_amount=inc["合計"],
            membership_fee=inc["会費"],
            personal_donation=inc["個人寄附"],
            corporate_donation=inc["法人寄附"],
            political_org_donation=inc["政治団体寄附"]
        )
        session.add(income_sum)

        # 3) loans
        for obj in inc["借入金"]:
            session.add(Loan(
                org_id=org.id,
                lender=obj["借入先"],
                amount=obj["金額"],
                date=datetime.strptime(obj["日付"], "%Y-%m-%d").date()
            ))

        # 4) other_incomes
        for obj in inc["その他の収入"]:
            session.add(OtherIncome(
                org_id=org.id,
                item=obj.get("項目"),
                amount=obj.get("金額", 0),
                source=obj.get("出所"),
                date=datetime.strptime(obj["日付"], "%Y-%m-%d").date() if obj.get("日付") else None
            ))

        # 5) expense_summary & routine_expenses
        exp_sum = data["支出"]
        session.add(ExpenseSummary(org_id=org.id, total_amount=exp_sum["合計"]))
        routine = exp_sum["経常経費"]
        session.add(RoutineExpense(
            org_id=org.id,
            total_amount=routine["合計"],
            personnel=routine["人件費"],
            utilities=routine["光熱水費"],
            supplies=routine["備品消耗品費"],
            office_rent=routine["事務所費"]
        ))

        # 6) political_activity_expense + details
        pa = exp_sum["政治活動費"]
        pae = PoliticalActivityExpense(org_id=org.id, total_amount=pa["合計"])
        session.add(pae)
        session.flush()  # pae.id を取得
        # 各サブカテゴリ
        for subcat, block in pa.items():
            if subcat == "合計":
                continue
            details = block.get("明細", [])
            for obj in details:
                session.add(PoliticalActivityExpenseDetail(
                    political_activity_expense_id=pae.id,
                    minor_category=subcat,
                    purpose=obj.get("目的"),
                    amount=obj.get("金額", 0),
                    date=datetime.strptime(obj["日付"], "%Y-%m-%d").date(),
                    payee=obj.get("支出先"),
                    location=obj.get("所在地")
                ))

        # 7) donors
        for obj in data["寄附者一覧"]:
            session.add(Donor(
                org_id=org.id,
                name=obj.get("氏名"),
                amount=obj.get("金額", 0),
                address=obj.get("住所"),
                date=datetime.strptime(obj["日付"], "%Y-%m-%d").date()
            ))

        session.commit()
        print("データを挿入しました。")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# --- 使用例 ---
if __name__ == "__main__":
    load_and_insert("output.json")
