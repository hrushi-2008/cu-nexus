import base64
import html
import os
import streamlit as st
from storage import load_network, save_network

LOGO_PATH = "logo.png"

st.set_page_config(
    page_title="CU-Nexus | Chanakya University",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🎓",
    layout="wide",
)


@st.cache_resource
def get_shared_network():
    """Single shared CampusNetwork instance across all active users/tabs."""
    return load_network()


# Smart geometric typography + WhatsApp/Instagram-style chat bubble styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, p, input, textarea, select, button, label, .stMarkdown, .stText, [data-testid="stWidgetLabel"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    h1, h2, h3, h4 {
        font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif !important;
        letter-spacing: -0.02em !important;
        font-weight: 700 !important;
    }
    h3 {
        font-size: 1.22rem !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.5rem !important;
    }
    .sec-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.015em;
        margin: 8px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .conn-card {
        padding: 13px 15px;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.24);
        background: linear-gradient(145deg, rgba(148, 163, 184, 0.08), rgba(148, 163, 184, 0.03));
        margin-bottom: 10px;
    }
    .conn-name {
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    .conn-handle {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.84rem;
        font-weight: 500;
        opacity: 0.72;
    }
    .conn-meta {
        font-size: 0.87rem;
        margin-top: 4px;
        opacity: 0.88;
    }
    .skill-pill {
        display: inline-block;
        padding: 2px 9px;
        margin: 6px 4px 0 0;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 600;
        background-color: rgba(59, 130, 246, 0.16);
        color: #60a5fa;
    }

    /* --- WHATSAPP / INSTAGRAM STYLE CHAT BUBBLES --- */
    .chat-header-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        border-radius: 12px;
        background: rgba(148, 163, 184, 0.10);
        border: 1px solid rgba(148, 163, 184, 0.20);
        margin-bottom: 12px;
    }
    .chat-avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563eb, #06b6d4);
        color: #ffffff;
        font-weight: 700;
        font-size: 0.95rem;
        margin-right: 10px;
    }
    .chat-row-me {
        display: flex;
        justify-content: flex-end;
        margin: 4px 0;
    }
    .chat-row-other {
        display: flex;
        justify-content: flex-start;
        margin: 4px 0;
    }
    .bubble-me {
        max-width: 78%;
        padding: 9px 13px 6px 13px;
        border-radius: 16px 16px 4px 16px;
        background: linear-gradient(135deg, #005c4b, #047857);
        color: #ffffff;
        font-size: 0.94rem;
        line-height: 1.4;
        box-shadow: 0 1px 2px rgba(0,0,0,0.22);
        word-wrap: break-word;
    }
    .bubble-other {
        max-width: 78%;
        padding: 9px 13px 6px 13px;
        border-radius: 16px 16px 16px 4px;
        background-color: #1f2937;
        border: 1px solid rgba(148, 163, 184, 0.22);
        color: #f8fafc;
        font-size: 0.94rem;
        line-height: 1.4;
        box-shadow: 0 1px 2px rgba(0,0,0,0.18);
        word-wrap: break-word;
    }
    .bubble-sender {
        font-size: 0.74rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 2px;
    }
    .bubble-time {
        font-size: 0.68rem;
        opacity: 0.72;
        text-align: right;
        margin-top: 3px;
    }
    .chat-sys-pill {
        text-align: center;
        margin: 8px auto;
        padding: 4px 12px;
        border-radius: 999px;
        background: rgba(148, 163, 184, 0.14);
        font-size: 0.76rem;
        opacity: 0.85;
        width: fit-content;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_brand_banner(subtitle: str = "Chanakya University Campus Network", logo_width: int = 86):
    if os.path.exists(LOGO_PATH):
        l_col, t_col = st.columns([1, 5])
        with l_col:
            st.image(LOGO_PATH, width=logo_width)
        with t_col:
            st.title("CU-Nexus")
            st.caption(subtitle)
    else:
        st.title("🎓 CU-Nexus")
        st.caption(subtitle)


def render_connection_action(net, me: str, target: str, key_prefix: str):
    if target == me:
        st.caption("👤 Your profile")
    elif target in net.adj_list[me]:
        st.success("✅ Connected")
    elif target in net.pending_incoming[me]:
        if st.button("Accept Request", key=f"{key_prefix}_acc_{target}", type="primary"):
            ok, msg = net.accept_request(me, target)
            save_network(net)
            st.toast(msg)
            st.rerun()
    elif me in net.pending_incoming[target]:
        if st.button("Cancel Request", key=f"{key_prefix}_can_{target}"):
            net.reject_or_cancel_request(target, me)
            save_network(net)
            st.toast("Request cancelled.")
            st.rerun()
    else:
        if st.button("➕ Connect", key=f"{key_prefix}_con_{target}", type="primary"):
            ok, msg = net.send_request(me, target)
            save_network(net)
            st.toast(msg)
            st.rerun()


def render_post_image(image_b64: str | None):
    if image_b64:
        try:
            st.image(base64.b64decode(image_b64), use_container_width=True)
        except Exception:
            pass


# --- LIVE AUTO-REFRESH FRAGMENTS (POLL EVERY 3 SECONDS WITHOUT CLEARING INPUTS) ---
@st.fragment(run_every="3s")
def live_notifications_panel(me: str):
    shared_net = get_shared_network()
    user_notifs = shared_net.get_notifications(me)
    prev_count = st.session_state.get("last_notif_count", len(user_notifs))
    if len(user_notifs) > prev_count:
        st.toast(f"🔔 {user_notifs[-1]}")
    st.session_state.last_notif_count = len(user_notifs)

    with st.expander(f"🔔 Notifications ({len(user_notifs)} unread)", expanded=len(user_notifs) > 0):
        if not user_notifs:
            st.caption("No new notifications.")
        else:
            for note in user_notifs:
                st.write(f"• {note}")
            if st.button("✅ Mark all as read", key="clear_notifs"):
                shared_net.clear_notifications(me)
                st.session_state.last_notif_count = 0
                save_network(shared_net)
                st.rerun(scope="fragment")


@st.fragment(run_every="3s")
def live_dm_messages_view(me: str, selected_peer: str):
    shared_net = get_shared_network()
    peer_obj = shared_net.users[selected_peer]
    messages = shared_net.get_direct_messages(me, selected_peer)
    with st.container(border=True):
        if not messages:
            st.caption(f"Say hi to {peer_obj.name}! Messages update automatically in real time.")
        for m in messages:
            if m["sender"] == me:
                b_col, d_col = st.columns([11, 1])
                with b_col:
                    st.markdown(
                        f"""
                        <div class="chat-row-me">
                            <div class="bubble-me">
                                {html.escape(m["text"])}
                                <div class="bubble-time">{html.escape(m["time_str"])} ✓✓</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with d_col:
                    if st.button("🗑️", key=f"del_dm_{m['id']}", help="Delete message"):
                        if shared_net.delete_direct_message(me, selected_peer, m["id"], me):
                            save_network(shared_net)
                            st.rerun(scope="fragment")
            else:
                st.markdown(
                    f"""
                    <div class="chat-row-other">
                        <div class="bubble-other">
                            {html.escape(m["text"])}
                            <div class="bubble-time">{html.escape(m["time_str"])}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


@st.fragment(run_every="3s")
def live_group_messages_view(me: str, selected_gid: str):
    shared_net = get_shared_network()
    active_group = shared_net.groups.get(selected_gid)
    if not active_group:
        return
    with st.container(border=True):
        for gm in active_group["messages"]:
            if gm["sender"] == "system":
                st.markdown(
                    f'<div class="chat-sys-pill">{html.escape(gm["text"])} • {html.escape(gm["time_str"])}</div>',
                    unsafe_allow_html=True,
                )
            elif gm["sender"] == me:
                gb_col, gd_col = st.columns([11, 1])
                with gb_col:
                    st.markdown(
                        f"""
                        <div class="chat-row-me">
                            <div class="bubble-me">
                                {html.escape(gm["text"])}
                                <div class="bubble-time">{html.escape(gm["time_str"])} ✓✓</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with gd_col:
                    if st.button("🗑️", key=f"del_gm_{gm['id']}", help="Delete message"):
                        if shared_net.delete_group_message(selected_gid, gm["id"], me):
                            save_network(shared_net)
                            st.rerun(scope="fragment")
            else:
                sender_name = shared_net.users[gm["sender"]].name if gm["sender"] in shared_net.users else gm["sender"]
                st.markdown(
                    f"""
                    <div class="chat-row-other">
                        <div class="bubble-other">
                            <div class="bubble-sender">{html.escape(sender_name)} (@{html.escape(gm["sender"])})</div>
                            {html.escape(gm["text"])}
                            <div class="bubble-time">{html.escape(gm["time_str"])}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


net = get_shared_network()

if "viewing_profile" not in st.session_state:
    st.session_state.viewing_profile = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "signin"
if "auth_notice" not in st.session_state:
    st.session_state.auth_notice = ""
if "editing_profile" not in st.session_state:
    st.session_state.editing_profile = False

if "current_user" not in st.session_state or st.session_state.current_user is None:
    saved_user = st.query_params.get("user", None)
    if saved_user and saved_user in net.users:
        st.session_state.current_user = saved_user
    else:
        st.session_state.current_user = None

# ==========================================
# 1. AUTHENTICATION FLOW
# ==========================================
if not st.session_state.current_user:
    render_brand_banner("Chanakya University Campus Network", logo_width=95)

    if st.session_state.auth_mode == "signin":
        st.subheader("Sign In to CU-Nexus")
        if st.session_state.auth_notice:
            st.success(st.session_state.auth_notice)
            st.session_state.auth_notice = ""

        u_in = st.text_input("Username", key="login_u")
        p_in = st.text_input("Password", type="password", key="login_p")
        if st.button("Sign In", type="primary"):
            if net.login(u_in, p_in):
                clean_u = u_in.strip().lower()
                st.session_state.current_user = clean_u
                st.query_params["user"] = clean_u
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.divider()
        st.write("Don't have an account yet?")
        if st.button("Create a new account"):
            st.session_state.auth_mode = "signup"
            st.rerun()

    elif st.session_state.auth_mode == "signup":
        st.subheader("Create a New CU-Nexus Account")
        new_u = st.text_input("Choose Unique Username (no spaces)")
        new_p = st.text_input("Choose Password", type="password")
        new_name = st.text_input("Full Name")
        new_prog = st.selectbox("Programme", ["B.Tech CSAI", "B.Tech EVE", "B.Tech EECS", "BCA", "MCA"])
        new_year = st.selectbox("Year", [1, 2, 3, 4])
        new_bio = st.text_area("Short Bio")

        preset_skills = ["Python", "C++", "Java", "DSA", "PyTorch", "React", "SQL", "Arduino", "Verilog", "MATLAB", "Other"]
        selected_skills = st.multiselect("Select Your Skills", preset_skills)
        custom_skills = []
        if "Other" in selected_skills:
            other_input = st.text_input("Enter other skills (comma-separated, e.g. Rust, Figma, Docker)")
            custom_skills = [s.strip() for s in other_input.split(",") if s.strip()]

        final_skills = [s for s in selected_skills if s != "Other"] + custom_skills

        col_sub, col_back = st.columns([1, 4])
        with col_sub:
            if st.button("Create Account", type="primary"):
                ok, msg = net.signup(new_u, new_p, new_name, new_prog, new_year, new_bio, final_skills)
                if ok:
                    save_network(net)
                    st.session_state.auth_notice = f"✅ Account '{new_u.strip().lower()}' created! Please sign in below."
                    st.session_state.auth_mode = "signin"
                    st.rerun()
                else:
                    st.error(msg)
        with col_back:
            if st.button("← Back to Sign In"):
                st.session_state.auth_mode = "signin"
                st.rerun()
    st.stop()

# ==========================================
# 2. ADMIN DASHBOARD
# ==========================================
me = st.session_state.current_user
if me not in net.users:
    st.session_state.current_user = None
    st.query_params.clear()
    st.rerun()

user_obj = net.users[me]

if user_obj.is_admin:
    top_l, top_r = st.columns([4, 1])
    with top_l:
        render_brand_banner(f"CU-Nexus Admin Dashboard • Signed in as @{me}", logo_width=70)
    with top_r:
        if st.button("Logout", key="adm_logout"):
            st.session_state.current_user = None
            st.session_state.auth_mode = "signin"
            st.query_params.clear()
            st.rerun()

    student_users = [u for u, obj in net.users.items() if not obj.is_admin]
    total_edges = sum(len(friends) for friends in net.adj_list.values()) // 2
    total_posts = sum(len(posts) for posts in net.user_posts.values())
    total_groups = len(net.groups)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Student Nodes (V)", len(student_users))
    m2.metric("Undirected Edges (E)", total_edges)
    m3.metric("Total Posts", total_posts)
    m4.metric("Active Groups", total_groups)

    st.divider()
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(["👥 Users", "📝 Posts", "🔗 Edges & Groups"])

    with admin_tab1:
        st.subheader("Registered Student Accounts")
        for u in sorted(student_users):
            u_info = net.users[u]
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{u_info.name}** (`@{u}`) — {u_info.programme}, Year {u_info.year}")
                c1.caption(f"Bio: {u_info.bio} | Skills: {', '.join(u_info.skills)} | Connections: {len(net.adj_list[u])}")
                if c2.button("Delete User", key=f"adm_del_u_{u}", type="primary"):
                    net.delete_user_account(u)
                    save_network(net)
                    st.toast(f"Deleted user @{u}")
                    st.rerun()

    with admin_tab2:
        st.subheader("All Posts Across Campus")
        all_posts = [p for posts in net.user_posts.values() for p in posts]
        all_posts.sort(key=lambda x: x["timestamp"], reverse=True)
        if not all_posts:
            st.info("No posts in the database.")
        for p in all_posts:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**@{p['author']}** • _{p['time_str']}_ • ❤️ {len(p.get('likes', set()))} | 💬 {len(p.get('comments', []))}")
                c1.write(p["content"])
                render_post_image(p.get("image_b64"))
                if c2.button("Delete Post", key=f"adm_del_p_{p['id']}"):
                    net.delete_post(p["author"], p["id"])
                    save_network(net)
                    st.toast("Post removed.")
                    st.rerun()

    with admin_tab3:
        st.subheader("Active Undirected Connections (Edges)")
        seen_edges = set()
        for u, friends in net.adj_list.items():
            for v in friends:
                edge = tuple(sorted((u, v)))
                if edge not in seen_edges:
                    seen_edges.add(edge)
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"🔗 **`@{edge[0]}`** $\leftrightarrow$ **`@{edge[1]}`**")
                    if c2.button("Remove Edge", key=f"adm_edge_{edge[0]}_{edge[1]}"):
                        net.remove_connection(edge[0], edge[1])
                        save_network(net)
                        st.rerun()

        st.divider()
        st.subheader("Campus Groups")
        for gid, grp in list(net.groups.items()):
            c1, c2 = st.columns([4, 1])
            c1.write(f"👥 **{grp['name']}** ({grp['topic']}) — Members: {', '.join(sorted(grp['members']))}")
            if c2.button("Delete Group", key=f"adm_grp_{gid}"):
                net.groups.pop(gid, None)
                save_network(net)
                st.rerun()
    st.stop()

# ==========================================
# 3. REGULAR STUDENT DASHBOARD
# ==========================================
hdr_logo, hdr_user, hdr_logout = st.columns([1, 4, 1])
with hdr_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=62)
with hdr_user:
    st.markdown(f"### CU-Nexus • {user_obj.name} (`@{me}`)")
    st.caption(f"{user_obj.programme} • Year {user_obj.year} • {len(net.adj_list[me])} Connections")
with hdr_logout:
    if st.button("Logout", key="top_logout"):
        st.session_state.current_user = None
        st.session_state.viewing_profile = None
        st.session_state.editing_profile = False
        st.session_state.auth_mode = "signin"
        st.query_params.clear()
        net.nav_stack.clear()
        st.rerun()

# Real-time auto-updating notifications panel
live_notifications_panel(me)

tab_feed, tab_network, tab_chat, tab_search, tab_profile = st.tabs([
    "🏠 Feed", "🤝 Network", "💬 Chat & Groups", "🔍 Search", "👤 Profile"
])

# ==========================================
# FEED TAB
# ==========================================
with tab_feed:
    st.markdown('<div class="sec-title">✍️ Share a Project Idea or Update</div>', unsafe_allow_html=True)
    post_text = st.text_area("What are you building?", placeholder="Pitch an idea, ask for lab help, or share progress...")
    post_tags = st.text_input("Tags", placeholder="#CSAI #Hackathon")
    uploaded_photo = st.file_uploader(
        "📷 Attach a Photo (optional)",
        type=["png", "jpg", "jpeg", "webp"],
        key="post_photo_uploader",
    )
    if uploaded_photo is not None:
        st.image(uploaded_photo, caption="Photo Preview", width=280)

    if st.button("Post Update", type="primary"):
        if post_text.strip() or uploaded_photo is not None:
            img_b64 = None
            if uploaded_photo is not None:
                img_b64 = base64.b64encode(uploaded_photo.getvalue()).decode("utf-8")
            net.create_post(me, post_text, post_tags, image_b64=img_b64)
            save_network(net)
            st.success("Published!")
            st.rerun()
        else:
            st.warning("Write something or attach a photo before posting.")

    st.divider()
    st.markdown('<div class="sec-title">📰 Recent Network Posts</div>', unsafe_allow_html=True)
    feed_posts = net.get_home_feed(me)
    if not feed_posts:
        st.info("No posts yet. Connect with peers or publish your first idea!")
    for p in feed_posts:
        if p["author"] not in net.users:
            continue
        author_user = net.users[p["author"]]
        likes_set = p.setdefault("likes", set())
        comments_list = p.setdefault("comments", [])
        is_liked = me in likes_set

        with st.container(border=True):
            st.markdown(f"**{author_user.name}** (`@{p['author']}`) • _{p['time_str']}_")
            if p["content"]:
                st.write(p["content"])
            render_post_image(p.get("image_b64"))
            if p["tags"]:
                st.caption(p["tags"])

            like_label = f"❤️ Liked ({len(likes_set)})" if is_liked else f"🤍 Like ({len(likes_set)})"
            if st.button(like_label, key=f"like_{p['id']}"):
                net.toggle_like(p["author"], p["id"], me)
                save_network(net)
                st.rerun()

            with st.expander(f"💬 Comments ({len(comments_list)})"):
                if not comments_list:
                    st.caption("No comments yet. Start the discussion!")
                for c in comments_list:
                    st.markdown(f"**@{c['author']}** _{c['time_str']}_: {c['text']}")

                c_in, c_btn = st.columns([4, 1])
                with c_in:
                    new_comment = st.text_input(
                        "Write a comment...",
                        key=f"c_in_{p['id']}",
                        label_visibility="collapsed",
                        placeholder="Write a comment...",
                    )
                with c_btn:
                    if st.button("Send", key=f"c_btn_{p['id']}"):
                        if net.add_comment(p["author"], p["id"], me, new_comment):
                            save_network(net)
                            st.rerun()

# ==========================================
# NETWORK / CONNECTIONS TAB
# ==========================================
with tab_network:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="sec-title">📥 Pending Requests ({len(net.pending_incoming[me])})</div>', unsafe_allow_html=True)
        if not net.pending_incoming[me]:
            st.caption("No incoming connection requests right now.")
        for sender in list(net.pending_incoming[me]):
            if sender not in net.users:
                continue
            s_user = net.users[sender]
            st.markdown(
                f"""
                <div class="conn-card">
                    <div class="conn-name">{html.escape(s_user.name)} <span class="conn-handle">@{html.escape(sender)}</span></div>
                    <div class="conn-meta">🎓 {html.escape(s_user.programme)} • Year {s_user.year}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            c_acc, c_rej, _ = st.columns([1, 1, 2])
            if c_acc.button("Accept", key=f"acc_{sender}", type="primary"):
                net.accept_request(me, sender)
                save_network(net)
                st.rerun()
            if c_rej.button("Reject", key=f"rej_{sender}"):
                net.reject_or_cancel_request(me, sender)
                save_network(net)
                st.rerun()

        st.divider()
        st.markdown(f'<div class="sec-title">✅ My Connections ({len(net.adj_list[me])})</div>', unsafe_allow_html=True)
        if not net.adj_list[me]:
            st.caption("You haven't connected with anyone yet. Use Search or Recommendations to connect!")
        for friend in sorted(list(net.adj_list[me])):
            if friend not in net.users:
                continue
            f_user = net.users[friend]
            pills = "".join(f'<span class="skill-pill">{html.escape(sk)}</span>' for sk in f_user.skills)
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(
                    f"""
                    <div class="conn-card">
                        <div class="conn-name">{html.escape(f_user.name)} <span class="conn-handle">@{html.escape(friend)}</span></div>
                        <div class="conn-meta">🎓 {html.escape(f_user.programme)} • Year {f_user.year}</div>
                        <div>{pills if pills else '<span class="conn-handle">No skills listed</span>'}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c2:
                st.write("")
                if st.button("Remove", key=f"rem_{friend}"):
                    net.remove_connection(me, friend)
                    save_network(net)
                    st.rerun()

    with col2:
        st.markdown('<div class="sec-title">✨ Teammates You May Know</div>', unsafe_allow_html=True)
        recs = net.recommend_teammates(me)
        if not recs:
            st.caption("You're already connected with all recommended peers!")
        for cand, score, shared_skills in recs:
            c_user = net.users[cand]
            mutuals = net.get_mutual_connections(me, cand)
            pills = "".join(f'<span class="skill-pill">{html.escape(sk)}</span>' for sk in c_user.skills)
            st.markdown(
                f"""
                <div class="conn-card">
                    <div class="conn-name">{html.escape(c_user.name)} <span class="conn-handle">@{html.escape(cand)}</span> • Match: {score}</div>
                    <div class="conn-meta">🎓 {html.escape(c_user.programme)} • Mutuals: {len(mutuals)} ({html.escape(', '.join(mutuals)) if mutuals else 'None'})</div>
                    <div>{pills}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if me in net.pending_incoming[cand]:
                if st.button("Cancel Request", key=f"can_{cand}"):
                    net.reject_or_cancel_request(cand, me)
                    save_network(net)
                    st.rerun()
            else:
                if st.button("➕ Connect", key=f"con_{cand}", type="primary"):
                    ok, msg = net.send_request(me, cand)
                    save_network(net)
                    st.toast(msg)
                    st.rerun()

# ==========================================
# LIVE AUTO-SYNCED CHAT & GROUPS TAB
# ==========================================
with tab_chat:
    chat_mode = st.radio(
        "Select Messaging Mode:",
        ["💬 Direct Messages (1-on-1)", "👥 Campus Groups"],
        horizontal=True,
    )

    if chat_mode == "💬 Direct Messages (1-on-1)":
        my_friends = sorted([f for f in net.adj_list[me] if f in net.users])
        if not my_friends:
            st.info("Connect with a classmate in the Network or Search tab first to start chatting!")
        else:
            selected_peer = st.selectbox(
                "Select Chat:",
                my_friends,
                format_func=lambda u: f"{net.users[u].name} (@{u})",
            )
            peer_obj = net.users[selected_peer]
            initial = peer_obj.name[0].upper() if peer_obj.name else "?"

            st.markdown(
                f"""
                <div class="chat-header-bar">
                    <div style="display:flex; align-items:center;">
                        <div class="chat-avatar">{html.escape(initial)}</div>
                        <div>
                            <div class="conn-name">{html.escape(peer_obj.name)}</div>
                            <div class="conn-handle">@{html.escape(selected_peer)} • {html.escape(peer_obj.programme)}</div>
                        </div>
                    </div>
                    <span class="skill-pill">● Live Sync</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Live 3-second polling message window (no manual refresh needed)
            live_dm_messages_view(me, selected_peer)

            with st.form(key=f"dm_form_{selected_peer}", clear_on_submit=True):
                in_col, send_col = st.columns([5, 1])
                with in_col:
                    dm_text = st.text_input(
                        "Message",
                        placeholder=f"Message {peer_obj.name}...",
                        label_visibility="collapsed",
                    )
                with send_col:
                    submitted = st.form_submit_button("➤", type="primary", use_container_width=True)
                if submitted and dm_text.strip():
                    ok, msg = net.send_direct_message(me, selected_peer, dm_text)
                    if ok:
                        save_network(net)
                        st.rerun()
                    else:
                        st.error(msg)

    else:
        with st.expander("➕ Create a New Group (Minimum 2 Members Required)", expanded=False):
            grp_name = st.text_input("Group Name", placeholder="e.g. Smart India Hackathon Team")
            grp_topic = st.text_input("Topic / Purpose", placeholder="Project collaboration, study group, club...")
            all_peers = sorted([u for u, obj in net.users.items() if u != me and not obj.is_admin])
            selected_members = st.multiselect(
                "Select Members (Pick at least 1 other member):",
                all_peers,
                format_func=lambda u: f"{net.users[u].name} (@{u}) — {net.users[u].programme}",
            )
            total_selected = 1 + len(selected_members)
            if total_selected < 2:
                st.caption("⚠️ Current group size: **1 member** (You). Select at least **1 more member** to create a group.")
            else:
                st.caption(f"✅ Ready to create group with **{total_selected} members**.")

            if st.button("Create Group", type="primary", disabled=(total_selected < 2)):
                ok, msg = net.create_group(me, grp_name, grp_topic, selected_members)
                if ok:
                    save_network(net)
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        my_groups = net.get_user_groups(me)
        if not my_groups:
            st.info("You are not in any groups yet. Create one above with at least 2 members!")
        else:
            group_map = {g["id"]: g for g in my_groups}
            selected_gid = st.selectbox(
                "Select Group:",
                list(group_map.keys()),
                format_func=lambda gid: f"{group_map[gid]['name']} ({len(group_map[gid]['members'])} members)",
            )
            active_group = group_map[selected_gid]
            grp_initial = active_group["name"][0].upper() if active_group["name"] else "G"

            g_hdr_col, g_leave_col = st.columns([5, 1])
            with g_hdr_col:
                st.markdown(
                    f"""
                    <div class="chat-header-bar">
                        <div style="display:flex; align-items:center;">
                            <div class="chat-avatar">{html.escape(grp_initial)}</div>
                            <div>
                                <div class="conn-name">{html.escape(active_group["name"])}</div>
                                <div class="conn-handle">{html.escape(active_group["topic"])} • {', '.join('@' + m for m in sorted(active_group['members']))}</div>
                            </div>
                        </div>
                        <span class="skill-pill">● Live Sync</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with g_leave_col:
                st.write("")
                if st.button("Leave", key=f"leave_grp_{selected_gid}"):
                    net.leave_group(selected_gid, me)
                    save_network(net)
                    st.rerun()

            addable = sorted([
                u for u, obj in net.users.items()
                if not obj.is_admin and u not in active_group["members"]
            ])
            if addable:
                with st.expander("➕ Add Members to Group", expanded=False):
                    add_c1, add_c2 = st.columns([4, 1])
                    with add_c1:
                        to_add = st.selectbox(
                            "Select student to add",
                            addable,
                            key=f"add_sel_{selected_gid}",
                            label_visibility="collapsed",
                            format_func=lambda u: f"{net.users[u].name} (@{u}) — {net.users[u].programme}",
                        )
                    with add_c2:
                        if st.button("Add", key=f"add_btn_{selected_gid}", type="primary", use_container_width=True):
                            ok, msg = net.add_group_member(selected_gid, me, to_add)
                            if ok:
                                save_network(net)
                                st.toast(msg)
                                st.rerun()
                            else:
                                st.error(msg)

            # Live 3-second polling group message window
            live_group_messages_view(me, selected_gid)

            with st.form(key=f"grp_form_{selected_gid}", clear_on_submit=True):
                gin_col, gsend_col = st.columns([5, 1])
                with gin_col:
                    g_text = st.text_input(
                        "Group message",
                        placeholder=f"Message {active_group['name']}...",
                        label_visibility="collapsed",
                    )
                with gsend_col:
                    g_submitted = st.form_submit_button("➤", type="primary", use_container_width=True)
                if g_submitted and g_text.strip():
                    ok, msg = net.send_group_message(selected_gid, me, g_text)
                    if ok:
                        save_network(net)
                        st.rerun()
                    else:
                        st.error(msg)

# ==========================================
# SEARCH TAB
# ==========================================
with tab_search:
    st.markdown('<div class="sec-title">🔍 Real-Time Prefix Search (Trie)</div>', unsafe_allow_html=True)
    search_mode = st.radio(
        "Search Students By:",
        ["Name or Username", "Technical Skill"],
        horizontal=True,
    )

    if search_mode == "Name or Username":
        query = st.text_input("Type a student's name or username prefix (e.g. 'a', 'di', 'ro'):")
        results = net.search_users(query) if query else []
    else:
        query = st.text_input("Type a skill prefix (e.g. 'py', 'ard', 'mat', 'ver'):")
        results = net.search_by_skill(query) if query else []

    if query:
        st.write(f"Found {len(results)} match(es):")
        for r in results:
            skills_preview = ", ".join(r.skills) if r.skills else "No skills listed"
            with st.container(border=True):
                c_info, c_view, c_conn = st.columns([3, 1, 1])
                with c_info:
                    st.markdown(f"**{r.name}** (`@{r.username}`) • {r.programme} (Year {r.year})")
                    st.caption(f"Skills: {skills_preview}")
                with c_view:
                    if st.button("View Profile", key=f"view_{r.username}"):
                        if st.session_state.viewing_profile and st.session_state.viewing_profile != r.username:
                            net.nav_stack.append(st.session_state.viewing_profile)
                        st.session_state.viewing_profile = r.username
                        st.rerun()
                with c_conn:
                    render_connection_action(net, me, r.username, "srch_row")

    if st.session_state.viewing_profile and st.session_state.viewing_profile in net.users:
        target = st.session_state.viewing_profile
        t_user = net.users[target]
        st.divider()
        if net.nav_stack and net.nav_stack[-1] in net.users:
            if st.button(f"⬅ Back to @{net.nav_stack[-1]} (Stack Pop)"):
                st.session_state.viewing_profile = net.nav_stack.pop()
                st.rerun()

        p_col1, p_col2 = st.columns([3, 1])
        with p_col1:
            st.markdown(f"### Profile: {t_user.name} (`@{target}`)")
            st.write(f"**Programme:** {t_user.programme} (Year {t_user.year}) | **Bio:** {t_user.bio}")
            st.write(f"**Skills:** {', '.join(t_user.skills) if t_user.skills else 'None'}")
        with p_col2:
            render_connection_action(net, me, target, "srch_prof")

        if target != me:
            deg, path = net.find_shortest_path_bfs(me, target)
            mutuals = net.get_mutual_connections(me, target)
            if deg != -1:
                st.success(f"**Degree of Connection:** {deg} | **Shortest Chain (BFS):** {' ➔ '.join(path)}")
            else:
                st.warning("No connection path exists yet.")
            st.info(f"**Mutual Connections ({len(mutuals)}):** {', '.join(mutuals) if mutuals else 'None'}")

# ==========================================
# PROFILE TAB
# ==========================================
with tab_profile:
    st.markdown('<div class="sec-title">🪪 Account Holder Details</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"### {user_obj.name}")
        st.write(f"**Username:** `@{me}`")
        st.write(f"**Programme:** {user_obj.programme}")
        st.write(f"**Year:** Year {user_obj.year}")
        st.write(f"**Bio:** {user_obj.bio if user_obj.bio else 'No bio added yet.'}")
        st.write(f"**Skills:** {', '.join(user_obj.skills) if user_obj.skills else 'None'}")
        st.write(f"**Total Connections:** {len(net.adj_list[me])}")

        if st.button("✏️ Edit Profile Details"):
            st.session_state.editing_profile = not st.session_state.editing_profile
            st.rerun()

    if st.session_state.editing_profile:
        with st.container(border=True):
            st.subheader("Edit Your Profile")
            edit_name = st.text_input("Full Name", value=user_obj.name)
            prog_options = ["B.Tech CSAI", "B.Tech EVE", "B.Tech EECS", "BCA", "MCA"]
            prog_idx = prog_options.index(user_obj.programme) if user_obj.programme in prog_options else 0
            edit_prog = st.selectbox("Programme", prog_options, index=prog_idx)
            year_options = [1, 2, 3, 4]
            year_idx = year_options.index(user_obj.year) if user_obj.year in year_options else 0
            edit_year = st.selectbox("Year", year_options, index=year_idx)
            edit_bio = st.text_area("Short Bio", value=user_obj.bio)

            preset_skills = ["Python", "C++", "Java", "DSA", "PyTorch", "React", "SQL", "Arduino", "Verilog", "MATLAB", "Other"]
            existing_presets = [s for s in user_obj.skills if s in preset_skills and s != "Other"]
            existing_custom = [s for s in user_obj.skills if s not in preset_skills]
            if existing_custom:
                existing_presets.append("Other")

            edit_selected = st.multiselect("Select Your Skills", preset_skills, default=existing_presets)
            edit_custom = []
            if "Other" in edit_selected:
                other_val = st.text_input("Other skills (comma-separated)", value=", ".join(existing_custom))
                edit_custom = [s.strip() for s in other_val.split(",") if s.strip()]

            updated_skills = [s for s in edit_selected if s != "Other"] + edit_custom

            c_save, c_cancel = st.columns([1, 4])
            with c_save:
                if st.button("Save Changes", type="primary"):
                    ok, msg = net.update_profile(me, edit_name, edit_prog, edit_year, edit_bio, updated_skills)
                    if ok:
                        save_network(net)
                        st.session_state.editing_profile = False
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            with c_cancel:
                if st.button("Cancel"):
                    st.session_state.editing_profile = False
                    st.rerun()

    st.divider()
    st.markdown('<div class="sec-title">📝 My Published Posts</div>', unsafe_allow_html=True)
    my_posts = list(reversed(net.user_posts[me]))
    if not my_posts:
        st.write("You haven't posted anything yet.")
    for p in my_posts:
        with st.container(border=True):
            if p["content"]:
                st.write(p["content"])
            render_post_image(p.get("image_b64"))
            st.caption(f"{p['time_str']} {p['tags']} • ❤️ {len(p.get('likes', set()))} | 💬 {len(p.get('comments', []))}")
            if st.button("Delete Post", key=f"del_{p['id']}"):
                net.delete_post(me, p["id"])
                save_network(net)
                st.rerun()

    st.divider()
    with st.expander("⚠️ Danger Zone: Delete Account"):
        st.warning("Deleting your profile permanently removes your account, connections, pending requests, and posts from the network.")
        confirm_del = st.checkbox("I confirm I want to permanently delete my account.")
        if st.button("Delete My Profile", type="primary", disabled=not confirm_del):
            net.delete_user_account(me)
            save_network(net)
            st.session_state.current_user = None
            st.session_state.viewing_profile = None
            st.session_state.editing_profile = False
            st.session_state.auth_mode = "signin"
            st.session_state.auth_notice = f"Your account '@{me}' has been permanently deleted."
            st.query_params.clear()
            st.rerun()