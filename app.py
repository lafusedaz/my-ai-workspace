import streamlit as st
import datetime

# 1. ตั้งค่าหน้าจอแบบกว้าง (Wide Mode) และชื่อระบบร้าน
st.set_page_config(layout="wide", page_title="Tripple Nine Garage Workspace", page_icon="⚙️")

# ซ่อนเมนูหลังบ้านที่ไม่จำเป็นเพื่อความสวยงาม
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# 2. ฐานข้อมูลจำลองภายในระบบ (เก็บค่าใน Session State เพื่อให้สามารถ เพิ่ม/ลบ ข้อมูลได้จริง)
if "users_db" not in st.session_state:
    st.session_state.users_db = [
        {"username": "manager", "password": "mgr999", "role": "Manager", "created_at": "2026-01-01 09:00"},
        {"username": "staff1", "password": "stf123", "role": "Staff", "created_at": "2026-01-02 10:30"},
        {"username": "staff2", "password": "stf123", "role": "Staff", "created_at": "2026-06-25 11:00"}
    ]

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"id": 1, "target": "ญข-9999 (Nissan Sylphy)", "detail": "แปลงโฉมเป็น Sentra ตรงรุ่น + พ่นสีน้ำเงินรอบคัน เกรดแห้งช้า 2K", "user": "staff1", "status": "กำลังทำ", "update_time": "2026-06-25 14:00", "notes": ""},
        {"id": 2, "target": "คุณกิตติ (BMW Serie 5)", "detail": "อัปเกรดบอดี้พาร์ท M Sport รอบคัน ทำสีดำเงาพรีเมียม", "user": "staff2", "status": "ปิด Job", "update_time": "2026-06-25 17:30", "notes": "ปิดโดย staff2: ติดตั้งพาร์ทเนียนสนิท ตรวจเช็กระบบเซนเซอร์รอบคันผ่านฉลาก ส่งมอบรถเรียบร้อย"},
    ]

if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"id": "PART-SYL-01", "name": "ชุดกันชนหน้า Sentra (สำหรับแปลงโฉม Sylphy)", "oem": "OEM-NISSAN-ST01", "price": 18500, "stock": 3, "img": "https://imageboss.me"},
        {"id": "CLR-2K-PREM", "name": "สีพ่นรถยนต์เกรดพรีเมียม แห้งช้า 2K (ระบบเต็ม)", "oem": "OEM-PAINT-2KPM", "price": 4500, "stock": 12, "img": "https://imageboss.me"},
        {"id": "PART-TEA-02", "name": "กันชนหลัง Altima (สำหรับแปลงโฉม Teana L33)", "oem": "OEM-NISSAN-AT02", "price": 16000, "stock": 2, "img": "https://imageboss.me"},
    ]

# 3. ระบบเช็กสิทธิ์บัญชีผู้ใช้งานจากฐานข้อมูล
def login_system():
    if "user_role" not in st.session_state:
        st.title("⚙️ Tripple Nine Garage System")
        st.caption("ระบบบริหารจัดการอู่คัสตอม บอดี้พาร์ท และทำสีพรีเมียม")
        st.subheader("🔒 กรุณาเข้าสู่ระบบ")
        
        username_input = st.text_input("ชื่อผู้ใช้งาน (Username):")
        password_input = st.text_input("รหัสผ่าน (Password):", type="password")
        
        if st.button("เข้าสู่ระบบ", use_container_width=True):
            user_found = next((u for u in st.session_state.users_db if u["username"] == username_input and u["password"] == password_input), None)
            if user_found:
                st.session_state.user_role = user_found["role"]
                st.session_state.username = user_found["username"]
                st.rerun()
            else:
                st.error("❌ ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง")
        return False
    return True

# เมื่อล็อกอินผ่าน
if login_system():
    role = st.session_state.user_role
    current_user = st.session_state.username
    
    # --- แถบหัวบนสุด (Header) ---
    col_head_l, col_head_r = st.columns()
    with col_head_l:
        st.markdown(f"🏁 **Tripple Nine Garage** | ผู้ใช้งาน: `{current_user}` ({role})")
    with col_head_r:
        if st.button("ออกจากระบบ 🏃‍♂️", use_container_width=True):
            del st.session_state.user_role
            del st.session_state.username
            st.rerun()
    st.divider()

    # --- เมนูแถบซ้ายมือ (Sidebar) ---
    if role == "Staff":
        menu = st.sidebar.radio("เมนูการทำงาน", ["📋 หน้าจอติดตามงาน", "📦 สินค้าหลังร้าน"])
    else:
        menu = st.sidebar.radio("เมนูการทำงาน", ["💬 แชตกลุ่ม 5 ที่ปรึกษา AI", "📋 หน้าจอติดตามงาน", "📦 จัดการคลังสินค้า", "👥 จัดการระบบ USER"])

    # ----------------------------------------------------
    # [MANAGER ONLY] -> เมนูจัดการระบบ USER 
    # ----------------------------------------------------
    if role == "Manager" and menu == "👥 จัดการระบบ USER":
        st.subheader("👥 ระบบบริหารจัดการพนักงาน (USER Management)")
        col_list, col_add = st.columns([2, 1.2])
        with col_list:
            st.write("📊 **รายชื่อพนักงานและสิทธิ์การใช้งานปัจจุบัน**")
            for u in st.session_state.users_db:
                with st.container(border=True):
                    c_u, c_r, c_t, c_b = st.columns([2, 1.5, 2, 1.2])
                    with c_u:
                        st.markdown(f"👤 User: **{u['username']}**")
                    with c_r:
                        st.markdown(f"ตำแหน่ง: `{u['role']}`")
                    with c_t:
                        st.caption(f"📅 วันที่สร้าง: {u['created_at']}")
                    with c_b:
                        if u["username"] == "manager":
                            st.write("")
                        else:
                            if st.button("❌ ลบ", key=f"del_user_{u['username']}", use_container_width=True):
                                st.session_state.users_db = [usr for usr in st.session_state.users_db if usr["username"] != u["username"]]
                                st.success(f"ลบพนักงาน {u['username']} สำเร็จ!")
                                st.rerun()
                                
        with col_add:
            st.write("➕ **เพิ่มผู้ใช้งานใหม่เข้าสู่ระบบ**")
            new_un = st.text_input("ชื่อผู้ใช้งานใหม่ (Username):")
            new_pw = st.text_input("รหัสผ่านใหม่ (Password):")
            new_role = st.selectbox("เลือกประเภทสิทธิ์การใช้งาน:", ["Staff", "Manager"])
            if st.button("บันทึกเพิ่มพนักงาน", use_container_width=True):
                if new_un and new_pw:
                    if any(usr["username"] == new_un for usr in st.session_state.users_db):
                        st.error("⚠️ ชื่อผู้ใช้งานนี้มีอยู่ในระบบแล้ว")
                    else:
                        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.session_state.users_db.append({
                            "username": new_un, "password": new_pw, "role": new_role, "created_at": now_str
                        })
                        st.success(f"เพิ่มสิทธิ์ {new_role} ชื่อ {new_un} เรียบร้อย!")
                        st.rerun()
                else:
                    st.error("⚠️ กรุณากรอกข้อมูลให้ครบถ้วนก่อนกดบันทึก")
    # ----------------------------------------------------
    # [STAFF & MANAGER] -> เมนูติดตามงาน (ตรงกลางจอ)
    # ----------------------------------------------------
    elif menu == "📋 หน้าจอติดตามงาน":
        st.subheader("📋 ตารางและฟอร์มติดตามงานซ่อม/แต่งรถ")
        with st.expander("➕ เปิด Job งานใหม่ (กรอกข้อมูล 3 ช่อง)", expanded=False):
            t_target = st.text_input("1. ชื่อลูกค้า หรือ ทะเบียนรถ:")
            t_detail = st.text_area("2. รายละเอียดงาน (เช่น รุ่นรถ / ของแต่ง / เรฟลูกค้า):")
            t_img = st.file_uploader("3. แนบรูปถ่ายตัวรถปัจจุบันหรือรูปเรฟ (ถ้ามี):", type=["png", "jpg", "jpeg"])
            
            if st.button("บันทึกเปิด Job งาน"):
                if t_target and t_detail:
                    new_id = len(st.session_state.tasks) + 1
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.tasks.append({
                        "id": new_id, "target": t_target, "detail": t_detail,
                        "user": current_user, "status": "กำลังทำ", "update_time": now_str, "notes": ""
                    })
                    st.success("เปิด Job สำเร็จ! ระบบอัพเดทผู้สร้างและวันที่ให้อัตโนมัติ")
                    st.rerun()

        st.write("---")
        filtered_tasks = st.session_state.tasks if role == "Manager" else [t for t in st.session_state.tasks if t["user"] == current_user]
        
        for idx, task in enumerate(filtered_tasks):
            with st.container(border=True):
                c1, c2, c3 = st.columns()
                with c1:
                    st.markdown(f"### 🚗 {task['target']}")
                    st.caption(f"ช่างผู้รับผิดชอบ: **{task['user']}**")
                    st.caption(f"🕒 อัปเดตล่าสุด: {task['update_time']}")
                with c2:
                    st.markdown(f"**🔧 รายละเอียดงาน:**\n{task['detail']}")
                    if task['notes']:
                        st.info(f"📝 ประวัติการปิด Job:\n{task['notes']}")
                with c3:
                    st.markdown(f"สถานะงาน: `{task['status']}`")
                    if task['status'] != "ปิด Job":
                        with st.popover("🔴 กดปิด Job งานนี้", use_container_width=True):
                            reason = st.text_input("ระบุเหตุผล/รายละเอียดการส่งมอบงาน (จำเป็น):", key=f"rs_{task['id']}")
                            if st.button("ยืนยันปิด Job ถาวร", key=f"btn_{task['id']}", use_container_width=True):
                                if reason:
                                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                    for t in st.session_state.tasks:
                                        if t["id"] == task["id"]:
                                            t["status"] = "ปิด Job"
                                            t["notes"] = f"ปิดโดย {current_user}: {reason}"
                                            t["update_time"] = now_str
                                    st.success("ปิด Job งานเรียบร้อย!")
                                    st.rerun()
                                else:
                                    st.error("⚠️ ห้ามปล่อยว่าง! กรุณาระบุรายละเอียดการจบงานก่อนครับ")

    # ----------------------------------------------------
    # [STAFF & MANAGER] -> เมนูสินค้าคลังหลังร้าน
    # ----------------------------------------------------
    elif menu in ["📦 สินค้าหลังร้าน", "📦 จัดการคลังสินค้า"]:
        st.subheader("📦 คลังบอดี้พาร์ทและอะไหล่หลังร้าน")
        search_query = st.text_input("🔍 ค้นหาบอดี้พาร์ท อะไหล่ หรือ รหัสสินค้า:")
        
        display_inv = st.session_state.inventory
        if search_query:
            display_inv = [i for i in display_inv if search_query.lower() in i["name"].lower() or search_query.lower() in i["id"].lower() or search_query.lower() in i["oem"].lower()]

        if role == "Manager":
            with st.expander("➕ เพิ่มบอดี้พาร์ท/สินค้าใหม่เข้าสต๊อค", expanded=False):
                p_id = st.text_input("รหัสสินค้า (SKU):")
                p_name = st.text_input("ชื่อบอดี้พาร์ท / สินค้า:")
                p_oem = st.text_input("รหัส OEM อ้างอิง:")
                p_price = st.number_input("ราคาขายปลีก (บาท):", min_value=0, value=0)
                p_stock = st.number_input("จำนวนสต๊อคคงเหลือ (ชิ้น):", min_value=0, value=0)
                if st.button("บันทึกเข้าคลังสินค้า", use_container_width=True):
                    if p_id and p_name:
                        st.session_state.inventory.append({
                            "id": p_id, "name": p_name, "oem": p_oem, "price": p_price, "stock": p_stock, "img": "https://placeholder.com"
                        })
                        st.success("เพิ่มพาร์ทเข้าคลังสำเร็จ!")
                        st.rerun()

        for item in display_inv:
            with st.container(border=True):
                img_col, info_col, action_col = st.columns()
                with img_col:
                    st.image(item["img"], width=110)
                with info_col:
                    st.markdown(f"### {item['name']}")
                    st.write(f"**รหัสสินค้า:** `{item['id']}` | **รหัส OEM อ้างอิง:** `{item['oem']}`")
                    st.write(f"💰 **ราคาปลีก:** {item['price']:,} บาท | 📦 **คงเหลือในสต๊อค:** {item['stock']} ชิ้น")
                with action_col:
                    if role == "Manager":
                        if st.button(f"❌ ลบพาร์ทนี้ออกจากระบบ", key=f"del_{item['id']}", use_container_width=True):
                            st.session_state.inventory = [i for i in st.session_state.inventory if i["id"] != item["id"]]
                            st.rerun()

    # ----------------------------------------------------
    # [MANAGER ONLY] -> แชตกลุ่มระดมสมอง 5 AI ที่ปรึกษา
    # ----------------------------------------------------
    elif menu == "💬 แชตกลุ่ม 5 ที่ปรึกษา AI":
        st.subheader("💬 ห้องระดมสมองบอร์ดบริหาร AI (Tripple Nine Garage Meeting)")
        st.caption("AI ทั้ง 5 ตัวจะแชตร่วมกัน เสนอไอเดียพร้อมกัน โดยอิงข้อมูลงานคัสตอมแปลงโฉม Sylphy, Teana และรถยุโรปหรู")

        chat_box = st.container(height=420)
        with chat_box:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(f"**{message['speaker']}:** {message['text']}")

        uploaded_file = st.file_uploader("แนบรูปถ่ายตัวรถ หรือภาพเรฟบอดี้พาร์ทเพื่อส่งให้ทีม AI วิเคราะห์:", type=["png", "jpg", "jpeg"])
        user_msg = st.chat_input("พิมพ์หัวข้อหรือคำสั่ง เพื่อให้ที่ปรึกษาทั้ง 5 ตัวช่วยกันวางแผน...")

        if user_msg:
            st.session_state.chat_history.append({"role": "user", "speaker": "Manager", "text": user_msg})
            
            r1 = f"🛠️ **ฝ่ายผู้เชี่ยวชาญยานยนต์**: สำหรับงาน '{user_msg}' ในรุ่นยอดฮิตของเราอย่าง Sylphy แปลง Sentra หรือ Teana แปลง Altima ต้องระวังจุดยึดพาร์ทเนียน ๆ นะครับ ส่วนรถยุโรปหรูอย่าง Benz, BMW หรือ Porsche ต้องตรวจเช็กไม่ให้ระบบเซนเซอร์เดิมที่กันชนเอ๋อหลังดัดแปลงครับ"
            r2 = f"📝 **ฝ่ายคอนเทนต์**: ได้ไอเดียเลยค่ะช่าง! เดี๋ยวทำคลิปสั้นลง TikTok ถ่ายแบบเจาะลึก Before & After สเต็ปการแปลงโฉมข้ามสายพันธุ์ คอนเทนต์แนว 'ศัลยกรรมรถยนต์' คนชอบดูมาก ยอดวิวพุ่งแน่นอน!"
            r3 = f"📣 **ฝ่ายการตลาด**: เสริมครับ! เราดึงยอดวิวจากคลิปทำแคมเปญชวนคนขับ Sylphy/Teana ทั่วประเทศมาอัปเกรดเปลี่ยนรถเก่าเป็นโฉมใหม่พรีเมียม และชูจุดเด่นเรื่องห้องอบสี 2K เฉพาะทางของเราเพื่อดึงกลุ่ม Benz/BMW เข้ามาทำสีพาร์ทด้วย"
            r4 = f"🎨 **ฝ่ายกราฟิกดีไซน์**: เดี๋ยวผมจัดทำภาพปกเพจเฟซบุ๊กและกราฟิกโปรโมตใหม่ คุมโทนหรูหราดุดันแนวสปอร์ตคาร์ เอาใจเจ้าของ Porsche และรถยุโรป วางภาพพาร์ทซ้าย-ขวาให้เห็นความเนี้ยบชัดเจนครับ"
            r5 = f"📊 **ฝ่ายวิเคราะห์ตลาด**: เทรนด์ปี 2026 นี้ ลูกค้าเน้นงานคัสตอมตามเรฟ (Tailor-made) สูงขึ้นมากครับ การที่เรามีอู่สีและดัดแปลงเองได้ครบวงจรแบบ Tripple Nine Garage ถือว่าได้เปรียบคู่แข่งในตลาดมากครับ"
            
            st.session_state.chat_history.append({"role": "assistant", "speaker": "AI ผู้เชี่ยวชาญยานยนต์", "text": r1})
            st.session_state.chat_history.append({"role": "assistant", "speaker": "AI คอนเทนต์", "text": r2})
            st.session_state.chat_history.append({"role": "assistant", "speaker": "AI การตลาด & โปรดักชัน", "text": r3})
            st.session_state.chat_history.append({"role": "assistant", "speaker": "AI กราฟิกดีไซน์", "text": r4})
            st.session_state.chat_history.append({"role": "assistant", "speaker": "AI วิเคราะห์ตลาด", "text": r5})
            
            new_id = len(st.session_state.tasks) + 1
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.tasks.append({
                "id": new_id, "target": "🎯 โปรเจกต์คัสตอมจากไอเดีย AI", "detail": f"ระดมสมองหัวข้อ: {user_msg}",
                "user": "AI_Automation", "status": "กำลังทำ", "update_time": now_str, "notes": ""
            })
            st.rerun()
