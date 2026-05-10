import streamlit as st
import pandas as pd
import json
from datetime import datetime

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="PHAN TACH - PRO", layout="centered")

st.markdown("""
    <style>
    .block-container { max-width: 650px !important; padding-top: 1rem !important; }
    .main-title { text-align: center; color: #1E3A8A; font-size: 22px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #1E3A8A; padding-bottom: 5px; }
    .stTable td, .stTable th { font-size: 10px !important; padding: 2px !important; text-align: center !important; font-weight: bold !important; border: 1px solid #eee !important; }
    .dan-box { padding: 10px; border-radius: 5px; font-family: monospace; font-size: 13px; font-weight: bold; margin-bottom: 5px; border: 1px solid #ddd; }
    .root-display { font-size: 11px; font-weight: bold; color: #d32f2f; text-align: center; background: #fff5f5; padding: 6px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #ffe3e3; }
    </style>
    <html lang="vi" class="notranslate" translate="no"></html>
    """, unsafe_allow_html=True)

# --- 2. KHỞI TẠO STATE ---
if 'dau' not in st.session_state:
    for k in ['dau','duoi','tong','hieu','cham']: st.session_state[k] = [0]*10
    st.session_state.bo = [0]*15; st.session_state.giap = [0]*12
    st.session_state.dang5 = [0]*5; st.session_state.cl4 = [0]*4; st.session_state.bt4 = [0]*4
    for k in ['d_cl','u_cl','t_cl','so_he','d_tb','u_tb','t_tb','h_tb']: st.session_state[k] = [0, 0]
    st.session_state.ky_quay, st.session_state.n1, st.session_state.n2 = 1, 10, 36
    st.session_state.rd, st.session_state.rk, st.session_state.rg = 0, 0, 0
    st.session_state.ls = []; st.session_state.use_root = False
    st.session_state.final_results = [] 

# --- 3. DỮ LIỆU GỐC ---
DANG_5 = {"KEP":[0,55,11,66,22,77,33,88,44,99,5,50,16,61,27,72,38,83,49,94], "SAT KEP":[1,10,12,21,23,32,34,43,45,54,56,65,67,76,78,87,89,98,9,90], "CACH 1":[2,20,8,80,13,31,19,91,24,42,35,53,46,64,57,75,79,97,68,86], "CACH 2":[3,30,18,81,25,52,47,74,69,96,7,70,14,41,29,92,36,63,58,85], "CACH 3":[4,40,6,60,15,51,17,71,28,82,26,62,37,73,39,93,48,84,59,95]}
CL_4 = {"CC":[0,22,44,66,88,2,20,4,40,6,60,8,80,24,42,26,62,28,82,46,64,48,84,68,86], "CL":[1,3,5,7,9,21,23,25,27,29,41,43,45,47,49,61,63,65,67,69,81,83,85,87,89], "LL":[11,33,55,77,99,13,31,15,51,17,71,19,91,35,53,37,73,39,93,57,75,59,95,79,97], "LC":[10,12,14,16,18,30,32,34,36,38,50,52,54,56,58,70,72,74,76,78,90,92,94,96,98]}
BT_4 = {"BB":[0,11,22,33,44,1,10,2,20,3,30,4,40,12,21,13,31,14,41,23,32,24,42,34,43], "BT":[5,6,7,8,9,15,16,17,18,19,25,26,27,28,29,35,36,37,38,39,45,46,47,48,49], "TB":[90,91,92,93,94,80,81,82,83,84,70,71,72,73,74,60,61,62,63,64,50,51,52,53,54], "TT":[55,66,77,88,99,56,65,57,75,58,85,59,95,67,76,68,86,69,96,78,87,79,97,89,98]}
BO_MAP = {"00":[0,5,50,55],"01":[1,10,6,60,51,15,56,65],"02":[2,20,7,70,52,25,57,75],"03":[3,30,8,80,53,35,58,85],"04":[4,40,9,90,54,45,59,95],"11":[11,16,61,66],"12":[12,21,17,71,62,26,67,76],"13":[13,31,18,81,63,36,68,86],"14":[14,41,19,91,64,46,69,96],"22":[22,27,72,77],"23":[23,32,28,82,73,37,78,87],"24":[24,42,29,92,74,47,79,97],"33":[33,38,83,88],"34":[34,43,39,93,84,48,89,98],"44":[44,49,94,99]}
GIAP_12 = {"TI":[0,12,24,36,48,60,72,84,96],"SUU":[1,13,25,37,49,61,73,85,97],"DAN":[2,14,26,38,50,62,74,86,98],"MAO":[3,15,27,39,51,63,75,87,99],"THIN":[4,16,28,40,52,64,76,88],"TY":[5,17,29,41,53,65,77,89],"NGO":[6,18,30,42,54,66,78,90],"MUI":[7,19,31,43,55,67,79,91],"THAN":[8,20,32,44,56,68,80,92],"DAU":[9,21,33,45,57,69,81,93],"TUAT":[10,22,34,46,58,70,82,94],"HOI":[11,23,35,47,59,71,83,95]}
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
ROOT_DATA = {1:{"cham":[1,6,0,5,2,7,3,8,4,9],"dau":[1,6,0,5,4,9,2,7,3,8],"duoi":[1,6,2,7,0,5,4,9,3,8],"tong":[1,6,2,7,4,9,0,5,3,8],"hieu":[0,5,1,6,2,7,4,9,3,8]},2:{"cham":[2,7,1,6,3,8,4,9,0,5],"dau":[2,7,1,6,5,0,3,8,4,9],"duoi":[2,7,3,8,1,6,5,0,4,9],"tong":[2,7,3,8,5,0,1,6,4,9],"hieu":[0,5,2,7,1,6,3,8,4,9]},3:{"cham":[3,8,2,7,4,9,0,5,1,6],"dau":[3,8,2,7,6,1,4,9,5,0],"duoi":[3,8,4,9,2,7,6,1,5,0],"tong":[3,8,4,9,1,6,2,7,0,5],"hieu":[0,5,3,8,4,9,1,6,2,7]},4:{"cham":[4,9,3,8,0,5,1,6,2,7],"dau":[4,9,3,8,7,2,5,0,6,1],"duoi":[4,9,5,0,3,8,7,2,6,1],"tong":[4,9,0,5,2,7,1,6,3,8],"hieu":[0,5,4,9,1,6,2,7,3,8]},5:{"cham":[5,0,4,9,2,7,1,6,3,8],"dau":[5,0,2,7,3,8,4,9,1,6],"duoi":[5,0,4,9,1,6,2,7,3,8],"tong":[5,0,8,3,2,7,4,9,1,6],"hieu":[0,5,1,6,4,9,2,7,3,8]},6:{"cham":[6,1,5,0,3,8,2,7,4,9],"dau":[6,1,5,0,9,4,7,2,8,3],"duoi":[6,1,7,2,5,0,9,4,8,3],"tong":[6,1,9,4,3,8,5,0,2,7],"hieu":[0,5,1,6,2,7,3,8,4,9]},7:{"cham":[7,2,6,1,4,9,3,8,0,5],"dau":[7,2,6,1,0,5,8,3,9,4],"duoi":[7,2,8,3,6,1,0,5,9,4],"tong":[7,2,0,5,4,9,6,1,3,8],"hieu":[0,5,2,7,3,8,4,9,1,6]},8:{"cham":[8,3,7,2,5,0,4,9,1,6],"dau":[8,3,7,2,1,6,9,4,0,5],"duoi":[8,3,9,4,7,2,1,6,0,5],"tong":[8,3,1,6,5,0,7,2,4,9],"hieu":[0,5,3,8,2,7,1,6,4,9]},9:{"cham":[9,4,8,3,6,1,5,0,2,7],"dau":[9,4,8,3,2,7,0,5,1,6],"duoi":[9,4,0,5,8,3,2,7,1,6],"tong":[9,4,2,7,6,1,8,3,5,0],"hieu":[0,5,4,9,3,8,2,7,1,6]}}

# --- 4. HELPERS ---
def find_idx(n, mapping):
    for i, nums in enumerate(mapping.values()):
        if n in nums: return i
    return -1

def get_root_val(s):
    try:
        t = sum(int(x) for x in str(s) if x.isdigit());
        while t > 9: t = sum(int(x) for x in str(t))
        return t
    except: return 0

# HÀM TÍNH TOÀN BỘ MA TRẬN
def recalculate_matrix():
    rd, rk, rg = st.session_state.rd, st.session_state.rk, st.session_state.rg
    res = []
    for i in range(100):
        d, du, t, h = i//10, i%10, (i//10+i%10)%10, (i//10-i%10+10)%10
        sk = st.session_state.dau[d]+st.session_state.duoi[du]+st.session_state.tong[t]+st.session_state.hieu[h]+ \
             ((st.session_state.cham[d]*2) if d==du else (st.session_state.cham[d]+st.session_state.cham[du]))+ \
             st.session_state.bo[find_idx(i, BO_MAP)]+st.session_state.giap[find_idx(i, GIAP_12)]+ \
             st.session_state.dang5[find_idx(i, DANG_5)]+st.session_state.cl4[find_idx(i, CL_4)]+st.session_state.bt4[find_idx(i, BT_4)]+ \
             st.session_state.d_cl[d%2]+st.session_state.u_cl[du%2]+st.session_state.t_cl[t%2]+ \
             st.session_state.d_tb[1 if d>=5 else 0]+st.session_state.u_tb[1 if du>=5 else 0]+ \
             st.session_state.t_tb[1 if t>=5 else 0]+st.session_state.h_tb[1 if h>=5 else 0]+ \
             st.session_state.so_he[1 if i not in SO_THUONG else 0]
        sr = 0
        if st.session_state.use_root:
            def rs(r, cat, v): return ROOT_DATA[r][cat].index(v) if r in ROOT_DATA else 0
            sr = sum(rs(r, c, v) for r in [rd,rk,rg] for c, v in [("dau",d),("duoi",du),("tong",t),("hieu",h),("cham",d),("cham",du)])
        res.append({"s": f"{d}{du}", "d": sk + sr})
    st.session_state.final_results = res

# HÀM XỬ LÝ KHI NHẤN NÚT CẬP NHẬT
def process_update():
    raw = st.session_state.gdb_in
    if not raw or len(raw) < 2: 
        st.warning("Vui lòng nhập GĐB trước!")
        return
    
    n = int(raw[-2:])
    dv, duv, tv, hv = n//10, n%10, (n//10+n%10)%10, (n//10-n%10+10)%10
    
    # 1. Cập nhật Bảng A
    for i in range(10):
        st.session_state.dau[i] = 0 if i==dv else st.session_state.dau[i]+1
        st.session_state.duoi[i] = 0 if i==duv else st.session_state.duoi[i]+1
        st.session_state.tong[i] = 0 if i==tv else st.session_state.tong[i]+1
        st.session_state.hieu[i] = 0 if i==hv else st.session_state.hieu[i]+1
        st.session_state.cham[i] = 0 if (i==dv or i==duv) else st.session_state.cham[i]+1
    b_idx, g_idx, d5_idx, c4_idx, b4_idx = find_idx(n, BO_MAP), find_idx(n, GIAP_12), find_idx(n, DANG_5), find_idx(n, CL_4), find_idx(n, BT_4)
    st.session_state.bo = [0 if i==b_idx else x+1 for i,x in enumerate(st.session_state.bo)]
    st.session_state.giap = [0 if i==g_idx else x+1 for i,x in enumerate(st.session_state.giap)]
    st.session_state.dang5 = [0 if i==d5_idx else x+1 for i,x in enumerate(st.session_state.dang5)]
    st.session_state.cl4 = [0 if i==c4_idx else x+1 for i,x in enumerate(st.session_state.cl4)]
    st.session_state.bt4 = [0 if i==b4_idx else x+1 for i,x in enumerate(st.session_state.bt4)]
    st.session_state.d_cl[dv%2]=0; st.session_state.d_cl[(dv+1)%2]+=1
    st.session_state.u_cl[duv%2]=0; st.session_state.u_cl[(duv+1)%2]+=1
    st.session_state.t_cl[tv%2]=0; st.session_state.t_cl[(tv+1)%2]+=1
    st.session_state.so_he[1 if n not in SO_THUONG else 0]=0; st.session_state.so_he[0 if n not in SO_THUONG else 1]+=1
    st.session_state.d_tb[1 if dv>=5 else 0]=0; st.session_state.d_tb[0 if dv>=5 else 1]+=1
    st.session_state.u_tb[1 if duv>=5 else 0]=0; st.session_state.u_tb[0 if duv>=5 else 1]+=1
    st.session_state.t_tb[1 if tv>=5 else 0]=0; st.session_state.t_tb[0 if tv>=5 else 1]+=1
    st.session_state.h_tb[1 if hv>=5 else 0]=0; st.session_state.h_tb[0 if hv>=5 else 1]+=1

    # 2. Cập nhật mã Root & Tính bảng B
    st.session_state.rd, st.session_state.rk, st.session_state.rg = get_root_val(st.session_state.date_in), get_root_val(st.session_state.ky_w_val), get_root_val(raw)
    recalculate_matrix()
    
    # 3. Lưu lịch sử (Check an toàn)
    if st.session_state.final_results:
        df_temp = pd.DataFrame(st.session_state.final_results).sort_values(by=["d", "s"]).reset_index(drop=True)
        vị_tri = df_temp[df_temp['s'] == f"{n:02d}"].index[0]+1
        st.session_state.ls.insert(0, {"Số về": f"{n:02d}", "Vị trí": vị_tri, "Kỳ": st.session_state.ky_w_val})

# --- 5. UI ---
st.markdown("<div class='main-title'>💎 PHAN TACH - PRO</div>", unsafe_allow_html=True)

with st.sidebar:
    if st.button("❌ RESET ALL"): st.session_state.clear(); st.rerun()

c1, c2, c3 = st.columns([1.5, 1.5, 1.8])
with c1: st.text_input("GĐB:", value="000000", key="gdb_in")
with c2: st.text_input("Ngày:", datetime.now().strftime("%d%m%Y"), key="date_in")
with c3: st.number_input("Kỳ:", value=st.session_state.ky_quay, key="ky_w_val", step=1)

st.toggle("CỘNG ĐIỂM ROOT", key="use_root", on_change=recalculate_matrix)
st.markdown(f"<div class='root-display'>Root: Ngày {st.session_state.rd} | Kỳ {st.session_state.rk} | GĐB {st.session_state.rg}</div>", unsafe_allow_html=True)
st.button("🔥 CẬP NHẬT TỔNG LỰC", on_click=process_update, type="primary", use_container_width=True)

tabs = st.tabs(["⚡ Dàn", "📊 Bảng A (Khan)", "🔢 Mã Root", "🎲 Bảng B", "🕒 Lịch Sử", "💾 Sao Lưu"])

with tabs[0]:
    if st.session_state.final_results:
        df_final = pd.DataFrame(st.session_state.final_results).sort_values(by=["d", "s"])
        cn1, cn2 = st.columns(2)
        with cn1:
            st.session_state.n1 = st.number_input("Dàn 1:", 1, 100, st.session_state.n1, key="n1_in")
            d1 = ", ".join(df_final.head(st.session_state.n1)["s"].tolist())
            st.markdown(f"<div class='dan-box' style='color:#2e7d32; background:#e8f5e9;'>{d1}</div>", unsafe_allow_html=True)
            st.code(d1, language=None)
        with cn2:
            st.session_state.n2 = st.number_input("Dàn 2:", 1, 100, st.session_state.n2, key="n2_in")
            d2 = ", ".join(df_final.head(st.session_state.n2)["s"].tolist())
            st.markdown(f"<div class='dan-box' style='color:#1565c0; background:#e3f2fd;'>{d2}</div>", unsafe_allow_html=True)
            st.code(d2, language=None)
    else: st.info("Nhấn 'CẬP NHẬT TỔNG LỰC' để lấy dàn.")

with tabs[1]:
    def show_kh(lbl, k, names):
        st.write(f"**{lbl}**")
        st.table(pd.DataFrame([st.session_state[k]], columns=names, index=["Khan"]))
    for l, k in [("ĐẦU","dau"),("ĐUÔI","duoi"),("TỔNG","tong"),("HIỆU","hieu"),("CHẠM","cham")]: show_kh(l, k, range(10))
    show_kh("BỘ", "bo", list(BO_MAP.keys())); show_kh("GIÁP", "giap", list(GIAP_12.keys()))
    show_kh("5 DẠNG", "dang5", list(DANG_5.keys()))
    show_kh("C/L 4", "cl4", list(CL_4.keys())); show_kh("B/T 4", "bt4", list(BT_4.keys()))
    st.write("**8 BIẾN PHỤ 50/50**")
    phu_data = {"D_CL":st.session_state.d_cl, "U_CL":st.session_state.u_cl, "T_CL":st.session_state.t_cl, "HE":st.session_state.so_he, "D_TB":st.session_state.d_tb, "U_TB":st.session_state.u_tb, "T_TB":st.session_state.t_tb, "H_TB":st.session_state.h_tb}
    st.table(pd.DataFrame(phu_data, index=["0","1"]))

with tabs[2]:
    st.write("**TRA ĐIỂM ROOT HIỆN TẠI**")
    for r_name, r_val in [("Ngày", st.session_state.rd), ("Kỳ", st.session_state.rk), ("GĐB", st.session_state.rg)]:
        if r_val in ROOT_DATA:
            st.write(f"Root {r_name} ({r_val})")
            st.table(pd.DataFrame(ROOT_DATA[r_val]).T)

with tabs[3]:
    if st.session_state.final_results:
        m_vals = [[next(x['d'] for x in st.session_state.final_results if x['s'] == f"{d}{du}") for du in range(10)] for d in range(10)]
        st.table(pd.DataFrame(m_vals, columns=range(10), index=range(10)))
    else: st.info("Nhấn 'CẬP NHẬT TỔNG LỰC' để xem Bảng B.")

with tabs[4]:
    if st.session_state.ls: st.table(pd.DataFrame(st.session_state.ls))
    else: st.info("Chưa có lịch sử.")

with tabs[5]:
    sv = {k: st.session_state[k] for k in ['dau','duoi','tong','hieu','cham','bo','giap','dang5','cl4','bt4','d_cl','u_cl','t_cl','so_he','d_tb','u_tb','t_tb','h_tb','ls','ky_quay']}
    st.download_button("📥 TẢI DỮ LIỆU", data=json.dumps(sv), file_name="backup.json", use_container_width=True)
    up = st.file_uploader("📤 UPLOAD", type="json")
    if up and st.button("🚀 XÁC NHẬN KHÔI PHỤC"):
        ld = json.load(up)
        for k, v in ld.items():
            if k in st.session_state: st.session_state[k] = v
        st.success("Dữ liệu đã nạp vào Bảng A!")
