
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="SubSentry (MVP)", layout="centered")

# Simple auth (no real security; for demo only)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "subs" not in st.session_state:
    st.session_state.subs = []

def login():
    st.session_state.logged_in = True
    st.session_state.user = st.session_state.username

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None

if not st.session_state.logged_in:
    st.title("SubSentry — Secure & Empowering (MVP Demo)")
    st.text("Sign in to manage your subscriptions (demo — session storage only)")
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password")
    if st.button("Login"):
        login()
else:
    st.sidebar.write(f"Signed in as: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        logout()

    st.title("Dashboard — SubSentry")
    st.write("Secure & Empowering — take control of recurring costs.")

    # Add subscription form
    with st.form("add_sub"):
        name = st.text_input("Subscription name (e.g., Netflix)")
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        period = st.selectbox("Billing period", ["Monthly", "Yearly"])
        next_renewal = st.date_input("Next renewal date", value=datetime.today().date())
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Add subscription")
        if submitted:
            st.session_state.subs.append({
                "name": name,
                "price": float(price),
                "period": period,
                "next_renewal": next_renewal.isoformat(),
                "notes": notes
            })
            st.success("Subscription added. You're covered — we'll remind you.")

    # Display subscriptions
    subs = st.session_state.subs
    if subs:
        df = pd.DataFrame(subs)
        # compute monthly equivalent
        def monthly_equiv(row):
            return row["price"] if row["period"]=="Monthly" else row["price"]/12.0
        df["monthly_eq"] = df.apply(monthly_equiv, axis=1)
        total_monthly = df["monthly_eq"].sum()
        total_annual = df.apply(lambda r: r["price"] if r["period"]=="Yearly" else r["price"]*12, axis=1).sum()
        st.metric("Total monthly (approx.)", f"${total_monthly:,.2f}")
        st.metric("Total annual (approx.)", f"${total_annual:,.2f}")

        st.subheader("Your subscriptions")
        st.dataframe(df[["name","price","period","next_renewal","notes"]])

        # Renewal alerts
        st.subheader("Upcoming renewals (next 7 days)")
        today = datetime.today().date()
        upcoming = []
        for i,row in df.iterrows():
            try:
                nr = datetime.fromisoformat(row["next_renewal"]).date()
                if 0 <= (nr - today).days <= 7:
                    upcoming.append(row.to_dict())
            except Exception:
                pass
        if upcoming:
            st.warning("You have renewals happening soon:")
            st.table(pd.DataFrame(upcoming)[["name","price","period","next_renewal"]])
        else:
            st.info("No renewals in the next 7 days.")

        # Export CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Export CSV", csv, "subscriptions.csv", "text/csv")
    else:
        st.info("No subscriptions yet — add one to get started.")
