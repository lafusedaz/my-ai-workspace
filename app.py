from streamlit_cookies_controller import CookieController
controller = CookieController()
import streamlit as st
import datetime
import requests
import json
import base64

st.set_page_config(
    layout="wide", 
    page_title="Tripple Nine Garage", 
    page_icon="⚙️",
    initial_sidebar_state="expanded"
)

# === วางแทรกตรงนี้เลยครับ (ชิดซ้ายสุดของหน้าจอ) ===
def convert_image_to_base64(uploaded_file):
    if uploaded_file is not None:
        try:
            import base64
            bytes_data = uploaded_file.getvalue()
            base64_str = base64.b64encode(bytes_data).decode("utf-8")
            return f"data:image/jpeg;base64,{base64_str}"
        except Exception:
            return None
    return None

# ซ่อนส่วนหัว เมนู เครดิต และล็อกให้ Sidebar กางออกถาวร
st.markdown(
    """
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stSidebarCollapseButton"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    </style>
    """, 
    unsafe_allow_html=True
)


# ปรับปรุงฟังก์ชันตัดปัญหาเรื่องการแปลงค่าคีย์ตัวพิมพ์ใหญ่และอักขระพิเศษ
def call_gemini(prompt_text, system_instruction):
    import base64
    or_key = st.secrets.get("openrouter_api_key", "")
    if not or_key: return "⚠️ กรุณาตั้งค่า openrouter_api_key ในระบบ Secrets ก่อนครับ"
    
    # ถอดรหัสลิงก์ท่อตรง OpenRouter เต็มรูปแบบ ป้องกันปัญหาเครื่องหมายบวกหรือข้อความขาด 100%
    encoded_url = "aHR0cHM6Ly9vcGVucm91dGVyLmFpL2FwaS92MS9jaGF0L2NvbXBsZXRpb25z"
    url = base64.b64decode(encoded_url).decode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {or_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "user", "content": f"สวมบทบาท: {system_instruction}\nคำถาม: {prompt_text}"}
        ]
    }
    try:
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code == 200:
            data = res.json()
            return data['choices'][0]['message']['content']
        else:
            return f"💡 AI กำลังโหลดข้อมูล กรุณาลองอีกครั้ง (Code {res.status_code})"
    except Exception as e: return f"❌ System Error: {str(e)}"

if "users_db" not in st.session_state:
    st.session_state.users_db = [
        {"username": "manager", "password": "mgr999", "role": "Manager", "created_at": "2026-01-01 09:00", "avatar": None},
        {"username": "staff1", "password": "stf123", "role": "Staff", "created_at": "2026-01-02 10:30", "avatar": None},
        {"username": "ผู้เชี่ยวชาญด้านชิ้นส่วนรถยนต์", "password": "-", "role": "AI Bot", "created_at": "SYSTEM", "avatar": "⚙️", "desc": "เน้นข้อมูลเทคนิคช่าง โครงสร้างรถยนต์คัสตอม และรหัสอะไหล่บอดี้พาร์ทตรงรุ่น"},
        {"username": "ผู้เชี่ยวชาญด้านการตลาด", "password": "-", "role": "AI Bot", "created_at": "SYSTEM", "avatar": "📣", "desc": "เน้นกลยุทธ์การหาลูกค้าเข้าอู่ จัดโปรโมชันแคมเปญ และวิเคราะห์คู่แข่งแต่งรถ"},
        {"username": "ผู้เชี่ยวชาญด้านคอนเท้นต์ครีเอทีฟ", "password": "-", "role": "AI Bot", "created_at": "SYSTEM", "avatar": "📝", "desc": "เน้นไอเดียคิดสคริปต์ถ่ายคลิปสั้นลง TikTok/Reels แนวแปลงโฉมรถ Before & After ให้ดึงดูดใจ"}

    ]
if "tasks" not in st.session_state:
    st.session_state.tasks = [{"id": 1, "target": "ญข-9999 (Sylphy)", "detail": "แปลงโฉมเป็น Sentra ตรงรุ่น + พ่นสีน้ำเงินรอบคัน 2K", "user": "staff1", "status": "กำลังทำ", "update_time": "2026-06-25 14:00", "notes": "", "timeline": []}]
if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"id": "PART-SYL-01", "name": "ชุดกันชนหน้า Sentra (สำหรับ Sylphy)", "oem": "OEM-NISSAN-ST01", "price": 18500, "stock": 3, "img": "https://placeholder.com"},
        {"id": "CLR-2K-PREM", "name": "สีพ่นรถยนต์เกรดพรีเมียม แห้งช้า 2K", "oem": "OEM-PAINT-2KPM", "price": 4500, "stock": 12, "img": "https://placeholder.com"}
    ]
if "chat_history" not in st.session_state: st.session_state.chat_history = []

cookie_user = controller.get("saved_username")
cookie_role = controller.get("saved_role")

if cookie_user and cookie_role and "user_role" not in st.session_state:
    st.session_state.user_role = cookie_role
    st.session_state.username = cookie_user

if "user_role" not in st.session_state:
   if "user_role" not in st.session_state:
    st.title("⚙️ Tripple Nine Garage System")
    un = st.text_input("Username:")
    pw = st.text_input("Password:", type="password")
    
    if st.button("เข้าสู่ระบบ", use_container_width=True):
        user = next((u for u in st.session_state.users_db if u["username"] == un and u["password"] == pw), None)
        if user: 
            st.session_state.user_role = user["role"]
            st.session_state.username = user["username"]
            
            expire_time = datetime.datetime.now() + datetime.timedelta(seconds=300)
            controller.set("saved_username", user["username"], expires=expire_time)
            controller.set("saved_role", user["role"], expires=expire_time)
            st.success("🔓 ยินดีต้อนรับเข้าสู่ระบบ!")
            st.rerun()
    
            st.error("❌ บัญชีหรือรหัสผ่านไม่ถูกต้อง")
            
    # คำสั่งย้ายมาอยู่แนวเดียวกับ st.title เพื่อล็อกหน้าจอให้ถูกต้องเด็ดขาด
    st.stop()

role, current_user = st.session_state.user_role, st.session_state.username
my_user_data = next((u for u in st.session_state.users_db if u["username"] == current_user), None)
    
col_hl, col_hr = st.columns(2)
with col_hl: st.markdown(f"🏁 **Tripple Nine Garage** | ผู้ใช้งาน: `{current_user}` ({role})")
with col_hr:
        if st.button("ออกจากระบบ 🏃‍♂️", use_container_width=True):
            del st.session_state.user_role
            del st.session_state.username
            controller.remove("saved_username")
            controller.remove("saved_role")
        st.rerun()

st.divider()

st.sidebar.subheader("👤 ข้อมูลส่วนตัว")
if my_user_data and my_user_data.get("avatar"): 
        st.sidebar.image(my_user_data["avatar"], width=70)
else: 
        st.sidebar.write("👤 *ยังไม่มีรูปโปรไฟล์*")
    
    # สร้างตัวแปรช่วยนับเพื่อนำไปเปลี่ยนคีย์ (ใช้ล้างกล่องอัปโหลดหลังบันทึก)
if "avatar_version" not in st.session_state:
        st.session_state.avatar_version = 0
        
uploaded_avatar = st.sidebar.file_uploader(
        "เปลี่ยนรูป Avatar ของคุณ:", 
        type=["png","jpg","jpeg"], 
        key=f"my_av_up_{st.session_state.avatar_version}"
    )
    
    # ใช้ปุ่มกดยืนยันเพื่อล็อกไม่ให้เกิดลูป Rerun ค้าง และแปลงไฟล์รูปภาพ
if uploaded_avatar and my_user_data:
        if st.sidebar.button("💾 ยืนยันเปลี่ยนรูปโปรไฟล์", use_container_width=True, type="primary"):
            img_base64 = convert_image_to_base64(uploaded_avatar)
            if img_base64:
                my_user_data["avatar"] = img_base64
                st.session_state.avatar_version += 1  # สลับคีย์เพื่อล้างค่ารูปค้าง
                st.sidebar.success("อัปเดตรูปสำเร็จ!")
                st.rerun()
            else:
                st.sidebar.error("ไม่สามารถประมวลผลรูปภาพได้")


        
st.sidebar.divider()
menu = st.sidebar.radio("เมนูการทำงาน", ["📋 หน้าจอติดตามงาน", "📦 สินค้าหลังร้าน"] if role == "Staff" else ["💬 แชตที่ปรึกษา AI", "📋 หน้าจอติดตามงาน", "📦 จัดการคลังสินค้า", "👥 จัดการระบบ USER"])

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
                    cav1, cav2 = st.columns(2)
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
                                                # ปุ่มลบงานถาวร โชว์เฉพาะ Manager เท่านั้น
                    if role == "Manager":
                        if c3.button("🗑️ ลบงานถาวร", key=f"del_task_{task['id']}", use_container_width=True, type="primary"):
                            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
                            st.rerun()


    elif menu in ["📦 สินค้าหลังร้าน", "📦 จัดการคลังสินค้า"]:
        st.subheader("📦 คลังบอดี้พาร์ทและอะไหล่หลังร้าน")
        q = st.text_input("🔍 ค้นหาตามชื่อสินค้าบางส่วน หรือ รหัสสินค้า:")
        inv = [i for i in st.session_state.inventory if q.lower() in i["name"].lower() or q.lower() in i["id"].lower()] if q else st.session_state.inventory
        if role == "Manager":
            with st.expander("➕ เพิ่มบอดี้พาร์ทใหม่เข้าสต๊อค"):
                p_id, p_name, p_oem = st.text_input("รหัสสินค้า:"), st.text_input("ชื่อสินค้า:"), st.text_input("รหัส OEM:")
                p_p, p_s = st.number_input("ราคาปลีก:", min_value=0), st.number_input("สต๊อค:", min_value=0)
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
                    

       # --- เมนู 4: ห้องแชตแยกที่ปรึกษา AI (เฉพาะ Manager - เวอร์ชันแก้ปัญหาหน้าจอว่าง) ---
    elif menu == "💬 แชตที่ปรึกษา AI" and role == "Manager":
        st.subheader("💬 ห้องประชุมปรึกษาผู้เชี่ยวชาญ AI (แยกคุยรายบุคคล)")
        
        # ดึงรายชื่อ AI Bot ทั้งหมด
        ai_bots = [u for u in st.session_state.users_db if u["role"] == "AI Bot"]
        ai_names = [bot["username"] for bot in ai_bots]
        
        if not ai_names:
            st.warning("⚠️ ไม่พบข้อมูลรายชื่อ AI Bot ในระบบ กรุณาเพิ่มข้อมูลระบบ USER ก่อนครับ")
        else:
            # ส่วนควบคุมด้านบน: เลือก AI และ ปุ่มล้างประวัติ
            col_menu_ai, col_clear_btn = st.columns([4, 1.2])
            with col_menu_ai:
                selected_bot_name = st.radio("เลือกผู้เชี่ยวชาญที่คุณต้องการปรึกษา:", options=ai_names, horizontal=True)
            with col_clear_btn:
                if st.button("♻️ ล้างประวัติแชตทั้งหมด", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
                    
                     # ค้นหาบอทที่เลือกอย่างปลอดภัย
            active_bot = next((b for b in ai_bots if b["username"] == selected_bot_name), ai_bots[0])
            
            if active_bot:
                st.info(f"{active_bot.get('avatar', '🤖')} **{active_bot['username']}**: {active_bot.get('desc', '')}")
                st.divider()
                
                # กรองข้อความให้แสดงเฉพาะที่คุยกันตรงสายงานของบอทแต่ละตัว
                filtered_history = [
                    m for m in st.session_state.chat_history 
                    if (m.get("speaker") == "Manager" and m.get("to_bot") == active_bot["username"]) 
                    or m.get("speaker") == active_bot["username"]
                ]
                
                # วนลูปแสดงข้อความแชตทั้งหมดในอดีต
                for m in filtered_history:
                    chat_role = "user" if m.get("speaker") == "Manager" else "assistant"
                    with st.chat_message(chat_role, avatar=active_bot["avatar"] if chat_role == "assistant" else None): 
                        st.write(f"**{m.get('speaker', 'Unknown')}:** {m.get('text', '')}")
                        if m.get("img"):
                            st.image(m["img"], width=250)
                
                # ใช้จำนวนประวัติแชตมาเปลี่ยนคีย์ เพื่อบังคับล้างรูปภาพในกล่อง file_uploader หลังกดส่งข้อความสำเร็จ
                chat_history_len = len(st.session_state.chat_history)
                chat_img = st.file_uploader(
                    "📸 แนบรูปภาพชิ้นส่วน/หน้างานซ่อม (ถ้ามี):", 
                    type=["png","jpg","jpeg"], 
                    key=f"img_up_{active_bot['username']}_{chat_history_len}"
                )
                
                # ช่องพิมพ์ข้อความแชตด้านล่างสุด
                user_msg = st.chat_input(f"พิมพ์ข้อความปรึกษาเชิงลึกกับ {active_bot['username']} ที่นี่...")
                
                if user_msg:
                    # แปลงภาพถ่ายหน้างานเป็น Base64 ป้องกันภาพหายหลังการรีรันหน้าจอ
                    img_data = convert_image_to_base64(chat_img) if chat_img else None
                    
                    # 1. บันทึกคำสั่งฝั่งผู้ใช้ล็อกเป้าหมายไปหาบอทตัวปัจจุบัน
                    st.session_state.chat_history.append({
                        "role": "user", 
                        "speaker": "Manager", 
                        "to_bot": active_bot["username"], 
                        "text": user_msg,
                        "img": img_data
                    })
                    
                    # 2. ตั้งค่าข้อกำหนดพฤติกรรม (System Prompt) ส่งไปประมวลผลร่วมกัน
                    base = "คุณคือที่ปรึกษาของอู่ Tripple Nine Garage ร้านแต่งรถคัสตอมแปลงโฉม Sylphy->Sentra, Teana->Altima และรถยุโรป Benz/BMW/Porsche ทำสีพรีเมียม 2K ตอบยาวไม่เกิน 2 ประโยค"
                    system_prompt = f"{base} จงสวมบทบาทเป็น {active_bot['username']} และเน้นตอบในส่วนงาน: {active_bot.get('desc', '')}"
                    
                    # 3. เรียกใช้งานโมเดลผ่าน OpenRouter API (Gemini)
                    with st.spinner(f"🔮 {active_bot['username']} กำลังวิเคราะห์แผนงาน..."):
                        ai_reply = call_gemini(user_msg, system_prompt)
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "speaker": active_bot["username"], 
                            "text": ai_reply
                        })
                    
                    # 4. บันทึกลงระบบตารางงานซ่อมหลักของร้านโดยอัตโนมัติ (AI Automation)
                    # หาค่า ID ล่าสุดอย่างปลอดภัยเพื่อป้องกัน ID ซ้ำซ้อน
                    new_task_id = max([t["id"] for t in st.session_state.tasks]) + 1 if st.session_state.tasks else 1
                    
                    st.session_state.tasks.append({
                        "id": new_task_id, 
                        "target": f"🎯 แผนงานจาก {active_bot['username']}", # แก้ไขคำสะกดเพี้ยน
                        "detail": f"บันทึกคำปรึกษา: {user_msg}\n\n🤖 สรุปคำแนะนำ: {ai_reply}", # นำคำตอบของ AI มาบันทึกเก็บลงตารางงานช่างด้วย
                        "user": "AI_Automation", 
                        "status": "กำลังทำ", 
                        "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 
                        "notes": "", 
                        "timeline": []
                    })
                    
                    # รีรันระบบเพื่อเคลียร์ช่องใส่รูปภาพและแสดงผลแชตข้อความล่าสุดทันที
                    st.rerun()
