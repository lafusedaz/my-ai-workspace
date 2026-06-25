import streamlit as st
import datetime, requests, json

st.set_page_config(layout="wide", page_title="Tripple Nine Garage", page_icon="⚙️")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;}</style>", unsafe_allow_html=True)

# ปรับปรุงฟังก์ชันตัดปัญหาเรื่องการแปลงค่าคีย์ตัวพิมพ์ใหญ่และอักขระพิเศษ
def call_gemini(prompt_text, system_instruction):
    or_key = st.secrets.get("openrouter_api_key", "")
    if not or_key: return "⚠️ กรุณาตั้งค่า openrouter_api_key ในระบบ Secrets ก่อนครับ"
    
    url = "https://openrouter.ai" + "/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {or_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [
            {"role": "user", "content": f"สวมบทบาท: {system_instruction}\nคำถาม: {prompt_text}"}
        ]
    }
    try:
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code == 200:
            return res.json()['choices']['message']['content']
        else:
            return f"💡 AI กำลังโหลดข้อมูล กรุณาลองอีกครั้ง (Code {res.status_code})"
    except Exception as e: return f"❌ System Error: {str(e)}"



if "users_db" not in st.session_state:
    st.session_state.users_db = [
        {"username": "manager", "password": "mgr999", "role": "Manager", "created_at": "2026-01-01 09:00", "avatar": None},
        {"username": "staff1", "password": "stf123", "role": "Staff", "created_at": "2026-01-02 10:30", "avatar": None},
        {"username": "AI ผู้เชี่ยวชาญยานยนต์", "password": "-", "role": "AI Bot", "created_at": "SYSTEM", "avatar": "⚙️", "desc": "เน้นเทคนิคช่าง โครงสร้างรถ และรหัสพาร์ทตรงรุ่น"},
        {"username": "AI คอนเทนต์", "password": "-", "role": "AI Bot", "created_at": "SYSTEM", "avatar": "📝", "desc": "เน้นไอเดียถ่ายคลิป TikTok/เพจ แนว Before&After"},
        {"username": "AI การตลาด & โปรดักชัน", "password": "-", "role": "AI Bot", "created_at": "SYSTEM", "avatar": "📣", "desc": "เน้นกลยุทธ์หาลูกค้าและจัดแคมเปญโปรโมชัน"},
        {"username": "AI กราฟิกดีไซน์", "password": "-", "role": "AI Bot", "created_at": "SYSTEM", "avatar": "🎨", "desc": "เน้นไอเดียทิศทางภาพ โทนสี ดุดันหรูหราเพื่อโฆษณา"},
        {"username": "AI วิเคราะห์ตลาด", "password": "-", "role": "AI Bot", "created_at": "SYSTEM", "avatar": "📊", "desc": "เน้นวิเคราะห์คู่แข่ง เทรนด์แต่งรถปี 2026 และพฤติกรรมลูกค้า"}
    ]
if "tasks" not in st.session_state:
    st.session_state.tasks = [{"id": 1, "target": "ญข-9999 (Sylphy)", "detail": "แปลงโฉมเป็น Sentra ตรงรุ่น + พ่นสีน้ำเงินรอบคัน 2K", "user": "staff1", "status": "กำลังทำ", "update_time": "2026-06-25 14:00", "notes": "", "timeline": []}]
if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"id": "PART-SYL-01", "name": "ชุดกันชนหน้า Sentra (สำหรับ Sylphy)", "oem": "OEM-NISSAN-ST01", "price": 18500, "stock": 3, "img": "https://placeholder.com"},
        {"id": "CLR-2K-PREM", "name": "สีพ่นรถยนต์เกรดพรีเมียม แห้งช้า 2K", "oem": "OEM-PAINT-2KPM", "price": 4500, "stock": 12, "img": "https://placeholder.com"}
    ]
if "chat_history" not in st.session_state: st.session_state.chat_history = []

if "user_role" not in st.session_state:
    st.title("⚙️ Tripple Nine Garage System")
    un = st.text_input("Username:")
    pw = st.text_input("Password:", type="password")
    if st.button("เข้าสู่ระบบ", use_container_width=True):
        user = next((u for u in st.session_state.users_db if u["username"] == un and u["password"] == pw), None)
        if user: st.session_state.user_role, st.session_state.username = user["role"], user["username"]; st.rerun()
        else: st.error("❌ บัญชีหรือรหัสผ่านไม่ถูกต้อง")
else:
    role, current_user = st.session_state.user_role, st.session_state.username
    my_user_data = next((u for u in st.session_state.users_db if u["username"] == current_user), None)
    
    col_hl, col_hr = st.columns(2)
    with col_hl: st.markdown(f"🏁 **Tripple Nine Garage** | ผู้ใช้งาน: `{current_user}` ({role})")
    with col_hr:
        if st.button("ออกจากระบบ 🏃‍♂️", use_container_width=True): del st.session_state.user_role, st.session_state.username; st.rerun()
    st.divider()

    st.sidebar.subheader("👤 ข้อมูลส่วนตัว")
    if my_user_data and my_user_data.get("avatar"): st.sidebar.image(my_user_data["avatar"], width=70)
    else: st.sidebar.write("👤 *ยังไม่มีรูปโปรไฟล์*")
    uploaded_avatar = st.sidebar.file_uploader("เปลี่ยนรูป Avatar ของคุณ:", type=["png","jpg","jpeg"], key="my_av_up")
    if uploaded_avatar and my_user_data: my_user_data["avatar"] = uploaded_avatar; st.sidebar.success("อัปเดตรูปสำเร็จ!"); st.rerun()
        
    st.sidebar.divider()
    menu = st.sidebar.radio("เมนูการทำงาน", ["📋 หน้าจอติดตามงาน", "📦 สินค้าหลังร้าน"] if role == "Staff" else ["💬 แชตกลุ่ม 5 ที่ปรึกษา AI", "📋 หน้าจอติดตามงาน", "📦 จัดการคลังสินค้า", "👥 จัดการระบบ USER"])

    if menu == "👥 จัดการระบบ USER" and role == "Manager":
        st.subheader("👥 ระบบบริหารจัดการพนักงานและ AI")
        cl, ca = st.columns([2, 1.2])
        with cl:
            for u in st.session_state.users_db:
                with st.container(border=True):
                    c_u, c_r, c_b = st.columns([3, 2, 1.5])
                    c_u.write(f"👤 **{u['username']}** ({u['created_at']})")
                    c_r.write(f"`{u['role']}`")
                    if u["role"] == "AI Bot":
                        with c_b.popover("✏️ แก้ชื่อ", use_container_width=True):
                            new_ai_name = st.text_input("ชื่อใหม่สำหรับ AI นี้:", value=u["username"], key=f"edit_ai_{u['username']}")
                            if st.button("บันทึกชื่อ", key=f"save_ai_{u['username']}") and new_ai_name: u["username"] = new_ai_name; st.rerun()
                    elif u["username"] != "manager" and c_b.button("❌ ลบ", key=f"d_{u['username']}", use_container_width=True):
                        st.session_state.users_db = [usr for usr in st.session_state.users_db if usr["username"] != u["username"]]; st.rerun()
        with ca:
            new_un, new_pw = st.text_input("New Username:"), st.text_input("New Password:")
            if st.button("บันทึกเพิ่มพนักงาน", use_container_width=True) and new_un and new_pw:
                st.session_state.users_db.append({"username": new_un, "password": new_pw, "role": "Staff", "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "avatar": None}); st.rerun()

    elif menu == "📋 หน้าจอติดตามงาน":
        st.subheader("📋 ระบบติดตามตารางงาน")
        with st.expander("➕ เปิด Job งานใหม่ (กรอกข้อมูล 3 ช่อง)"):
            t_target = st.text_input("1. ชื่อลูกค้า/ทะเบียนรถ:")
            t_detail = st.text_area("2. รายละเอียดงานซ่อม:")
            st.file_uploader("3. แนบรูปถ่าย (ถ้ามี):", type=["png", "jpg", "jpeg"])
            if st.button("บันทึกเปิด Job") and t_target and t_detail:
                st.session_state.tasks.append({"id": len(st.session_state.tasks)+1, "target": t_target, "detail": t_detail, "user": current_user, "status": "กำลังทำ", "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "notes": "", "timeline": []}); st.rerun()
        
        for task in (st.session_state.tasks if role == "Manager" else [t for t in st.session_state.tasks if t["user"] == current_user]):
            if "timeline" not in task: task["timeline"] = []
            with st.container(border=True):
                c1, c2, c3 = st.columns([2.2, 3, 1.5])
                with c1:
                    u_data = next((usr for usr in st.session_state.users_db if usr["username"] == task["user"]), None)
                    cav1, cav2 = st.columns()
                    if u_data and u_data.get("avatar"): cav1.image(u_data["avatar"], width=45)
                    else: cav1.markdown("### 👤")
                    with cav2:
                        st.markdown(f"### 🚗 {task['target']}")
                        st.caption(f"ช่างผู้รับผิดชอบ: **{task['user']}**\n🕒 อัปเดต: {task['update_time']}")
                with c2:
                    st.markdown(f"**🔧 รายละเอียดหลัก:**\n{task['detail']}")
                    if task['notes']: st.info(f"📝 *บันทึกปิด Job:* {task['notes']}")
                    if task['timeline']:
                        st.markdown("**📌 ประวัติการบันทึกงาน (Reply Timeline):**")
                        for t_node in task['timeline']:
                            tc1, tc2 = st.columns([0.5, 5])
                            u_node_data = next((usr for usr in st.session_state.users_db if usr["username"] == t_node["user"]), None)
                            if u_node_data and u_node_data.get("avatar"): tc1.image(u_node_data["avatar"], width=30)
                            else: tc1.write("👤")
                            tc2.caption(f"**{t_node['user']}** ({t_node['time']}): {t_node['msg']}")
                c3.markdown(f"สถานะ: `{task['status']}`")
                if task['status'] != "ปิด Job":
                    with c3.popover("💬 Update Job (Reply)", use_container_width=True):
                        up_msg = st.text_input("พิมพ์รายงานความคืบหน้า:", key=f"upmsg_{task['id']}")
                        up_file = st.file_uploader("แนบรูปความคืบหน้า (ถ้ามี):", type=["png","jpg","jpeg"], key=f"upfile_{task['id']}")
                        if st.button("บันทึกอัปเดต", key=f"upbtn_{task['id']}") and up_msg:
                            task['timeline'].append({"user": current_user, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "msg": up_msg, "has_img": up_file is not None})
                            task['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M"); st.rerun()
                    with c3.popover("🔴 ปิด Job", use_container_width=True):
                        reason = st.text_input("ระบุเหตุผลการปิดงาน:", key=f"r_{task['id']}")
                        if st.button("ยืนยัน", key=f"b_{task['id']}") and reason:
                            for t in st.session_state.tasks:
                                if t["id"] == task["id"]: t["status"], t["notes"], t["update_time"] = "ปิด Job", f"ปิดโดย {current_user}: {reason}", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.rerun()

    elif menu in ["📦 สินค้าหลังร้าน", "📦 จัดการคลังสินค้า"]:
        st.subheader("📦 คลังบอดี้พาร์ทและอะไหล่หลังร้าน")
        q = st.text_input("🔍 ค้นหาตามชื่อสินค้าบางส่วน หรือ รหัสสินค้า:")
        inv = [i for i in st.session_state.inventory if q.lower() in i["name"].lower() or q.lower() in i["id"].lower()] if q else st.session_state.inventory
        if role == "Manager":
            with st.expander("➕ เพิ่มบอดี้พาร์ทใหม่เข้าสต๊оค"):
                p_id, p_name, p_oem = st.text_input("รหัสสินค้า:"), st.text_input("ชื่อสินค้า:"), st.text_input("รหัส OEM:")
                p_p, p_s = st.number_input("ราคาปลีก:", min_value=0), st.number_input("สต๊оค:", min_value=0)
                p_img = st.file_uploader("แนบรูปภาพสินค้า:", type=["png","jpg","jpeg"])
                if st.button("บันทึกสินค้า") and p_id and p_name:
                    st.session_state.inventory.append({"id": p_id, "name": p_name, "oem": p_oem, "price": p_p, "stock": p_s, "img": p_img if p_img else "https://placeholder.com"}); st.rerun()
        for item in inv:
            with st.container(border=True):
                im, inf, act = st.columns([1, 4, 1.5])
                im.image(item["img"], width=90)
                inf.markdown(f"### {item['name']}\n**SKU:** `{item['id']}` | **OEM:** `{item['oem']}`\n💰 {item['price']:,} บาท | 📦 สต๊อค: {item['stock']} ชิ้น")
                if role == "Manager" and act.button("❌ ลบพาร์ท", key=f"del_{item['id']}", use_container_width=True):
                    st.session_state.inventory = [i for i in st.session_state.inventory if i["id"] != item["id"]]; st.rerun()

    elif menu == "💬 แชตกลุ่ม 5 ที่ปรึกษา AI" and role == "Manager":
        st.subheader("💬 ห้องประชุมบอร์ดบริหาร AI จริง (Real-time)")
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.write(f"**{m['speaker']}:** {m['text']}")
        user_msg = st.chat_input("พิมพ์หัวข้อปรึกษาเชิงลึกที่นี่...")
        if user_msg:
            st.session_state.chat_history.append({"role": "user", "speaker": "Manager", "text": user_msg})
            base = "คุณคือที่ปรึกษาของอู่ Tripple Nine Garage ร้านแต่งรถคัสตอมแปลงโฉม Sylphy->Sentra, Teana->Altima และรถยุโรป Benz/BMW/Porsche ทำสีพรีเมียม 2K ตอบยาวไม่เกิน 2 ประโยค"
            ai_bots = [u for u in st.session_state.users_db if u["role"] == "AI Bot"]
            for bot in ai_bots:
                st.session_state.chat_history.append({"role": "assistant", "speaker": bot["username"], "text": call_gemini(user_msg, f"{base} จงสวมบทบาทเป็น {bot['username']} และเน้น {bot['desc']}")})
            st.session_state.tasks.append({"id": len(st.session_state.tasks)+1, "target": "🎯 แผนงานจากระบบ AI", "detail": f"ระดมสมอง: {user_msg}", "user": "AI_Automation", "status": "กำลังทำ", "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "notes": "", "timeline": []})
            st.rerun()
