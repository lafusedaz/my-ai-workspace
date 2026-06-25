import streamlit as st

# 1. ตั้งค่าหน้าจอเว็บให้เป็นแบบเปิดกว้างเต็มจอ (Wide Mode)
st.set_page_config(layout="wide", page_title="My AI Workspace")

# 2. ปรับแต่งดีไซน์ด้วย CSS (ซ่อนเมนูที่ไม่จำเป็น)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. ระบบเช็กรหัสผ่านล็อกอิน (Login System)
def check_password():
    """ฟังก์ชันตรวจสอบรหัสผ่าน คืนค่า True ถ้ารหัสผ่านถูกต้อง"""
    def password_entered():
        correct_password = st.secrets.get("password", "mysecret123")
        if st.session_state["password_input"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.subheader("🔒 กรุณาเข้าสู่ระบบเพื่อใช้งาน")
        st.text_input("ใส่วากรหัสผ่านส่วนตัวของคุณเพื่อเปิด Workspace:", type="password", on_change=password_entered, key="password_input")
        return False
    elif not st.session_state["password_correct"]:
        st.subheader("🔒 กรุณาเข้าสู่ระบบเพื่อใช้งาน")
        st.text_input("ใส่วากรหัสผ่านส่วนตัวของคุณเพื่อเปิด Workspace:", type="password", on_change=password_entered, key="password_input")
        st.error("❌ รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
        return False
    else:
        return True

# เรียกใช้งานฟังก์ชันล็อกอิน
if check_password():

    # 4. จัดโครงสร้างข้อมูลจำลองในความจำ (Session State)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "tasks" not in st.session_state:
        st.session_state.tasks = [
            {"job": "สรุปรายงานการประชุมประจำสัปดาห์", "by": "วรรณา", "status": "สำเร็จ"},
            {"job": "แปลคู่มือเทคนิคภาษาคอมพิวเตอร์", "by": "เคนจิ", "status": "กำลังทำ"}
        ]

    # 5. ส่วนหัวของหน้าเว็บ (Header) และปุ่มออกจากระบบ
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.title("🤖 My Private AI Workspace")
        st.caption("ระบบแชตและตารางงานส่วนตัวของคุณ รันบนระบบคลาวด์เปิดใช้งานได้ทุกที่")
    with col_logout:
        if st.button("Log out 🏃‍♂️"):
            del st.session_state["password_correct"]
            st.router()
            
    st.divider()

    # 6. แบ่งหน้าจอออกเป็น 3 คอลัมน์หลักตามที่ต้องการ
    col1, col2, col3 = st.columns([1, 2, 1.5])

    # --- คอลัมน์ที่ 1: รายชื่อ AI (AI Roster) ---
    with col1:
        st.subheader("👥 รายชื่อผู้ช่วย AI")
        ai_choice = st.radio("เลือกคุยกับ AI เฉพาะทาง:", ["สมชาย (ผู้ช่วยทั่วไป)", "วรรณา (นักเขียน/สรุปงาน)", "เคนจิ (นักแปลภาษา)"])
        st.info(f"สถานะ: {ai_choice} พร้อมทำงาน")

    # --- คอลัมน์ที่ 2: ช่องแชต (Chat Interface) ---
    with col2:
        st.subheader(f"💬 ห้องแชต: {ai_choice}")
        
        chat_container = st.container(height=400)
        with chat_container:
            if not st.session_state.chat_history:
                st.write("👋 สวัสดีเจ้านาย! สั่งงานในช่องแชตหรือเพิ่มงานในตารางขวามือได้เลยครับ")
            for chat in st.session_state.chat_history:
                if chat["role"] == "user":
                    st.chat_message("user").write(chat["text"])
                else:
                    st.chat_message("assistant").write(chat["text"])

        user_query = st.chat_input("พิมพ์ข้อความหรือสั่งงานที่นี่...")
        if user_query:
            st.session_state.chat_history.append({"role": "user", "text": user_query})
            ai_reply = f"รับทราบคำสั่งครับเจ้านาย! ระบบกำลังประมวลผลคำสั่ง '{user_query}' ของคุณอย่างเป็นส่วนตัว..."
            st.session_state.chat_history.append({"role": "assistant", "text": ai_reply})
            st.rerun()

    # --- คอลัมน์ที่ 3: ตารางงาน (Task Table) ---
    with col3:
        st.subheader("📋 ตารางสถานะงาน")
        st.table(st.session_state.tasks)
        
        with st.expander("➕ เพิ่มงานใหม่ลงตาราง", expanded=False):
            new_job = st.text_input("ชื่องาน:")
            new_by = st.selectbox("ผู้รับผิดชอบ:", ["สมชาย", "วรรณา", "เคนจิ"])
            if st.button("บันทึกงาน"):
                if new_job:
                    st.session_state.tasks.append({"job": new_job, "by": new_by, "status": "รอดำเนินการ"})
                    st.success("เพิ่มงานสำเร็จ!")
                    st.rerun()
