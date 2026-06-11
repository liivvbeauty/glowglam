import re
import unicodedata
import urllib.parse
from io import StringIO

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="LIIVV Beauty | Glow Glam",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SPREADSHEET_ID = st.secrets.get("SPREADSHEET_ID", "")
CLIENT_SPREADSHEET_ID = st.secrets.get("CLIENT_SPREADSHEET_ID", SPREADSHEET_ID)

SHEET_NAME = st.secrets.get("SHEET_NAME", "Base_Glow_Glam")
CLIENT_SHEET_NAME = st.secrets.get("CLIENT_SHEET_NAME", "Clientes_Glow_Glam")
LOG_WEBAPP_URL = st.secrets.get("LOG_WEBAPP_URL", "")

DEFAULT_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq"
    f"?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"
)

CLIENTS_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{CLIENT_SPREADSHEET_ID}/gviz/tq"
    f"?tqx=out:csv&sheet={urllib.parse.quote(CLIENT_SHEET_NAME)}"
)

SHEET_URL = st.secrets.get("GOOGLE_SHEET_CSV_URL", DEFAULT_CSV_URL)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');

    .stApp { background-color: #F7F2F4; }
    .block-container { padding-top: 1.4rem; max-width: 1120px; }

    .liivv-header {
        background: linear-gradient(135deg, #7A3C4B 0%, #2B2B2B 100%);
        padding: 34px 18px 30px 18px;
        border-radius: 0 0 34px 34px;
        text-align: center;
        margin-bottom: 18px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    }

    .liivv-logo {
        font-family: 'Montserrat', Arial, sans-serif;
        font-size: 4.2rem;
        color: #EBA6A6;
        margin: 0;
        letter-spacing: 12px;
        line-height: 0.95;
        font-weight: 300;
    }

    .liivv-subtitle {
        font-family: 'Montserrat', sans-serif;
        color: #F7F2F4;
        font-size: 0.84rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-top: 10px;
        font-weight: 700;
    }

    .intro-card, .filter-card, .result-card {
        background: #FFFFFF;
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(43,43,43,0.08);
        border: 1px solid rgba(122,60,75,0.10);
        margin-bottom: 16px;
    }

    .intro-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.55rem;
        color: #7A3C4B;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .intro-text {
        font-family: 'Montserrat', sans-serif;
        color: #555;
        font-size: 0.96rem;
        line-height: 1.5;
        margin: 0;
    }

    .section-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        color: #7A3C4B;
        font-size: 1.08rem;
        margin-bottom: 12px;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #EBA6A6 0%, #7A3C4B 100%);
        color: white !important;
        border-radius: 999px;
        padding: 0.85rem 1.1rem;
        font-weight: 800;
        font-size: 1.02rem;
        width: 100%;
        border: none;
        box-shadow: 0 10px 20px rgba(122, 60, 75, 0.22);
        font-family: 'Montserrat', sans-serif;
    }

    div[data-baseweb="select"] > div {
        border-radius: 14px;
        border-color: rgba(122,60,75,0.22);
    }

    .look-title {
        font-family: 'Montserrat', sans-serif;
        color: #2B2B2B;
        font-size: 1.35rem;
        font-weight: 800;
        margin: 0;
    }

    .look-subtitle {
        font-family: 'Montserrat', sans-serif;
        color: #7A3C4B;
        font-size: 0.86rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        margin-top: 4px;
    }

    .badge {
        display:inline-block;
        margin: 8px 6px 6px 0;
        padding: 5px 11px;
        border-radius: 999px;
        background:#F7F2F4;
        color:#7A3C4B;
        font-size:0.78rem;
        font-family:Montserrat,sans-serif;
        font-weight:800;
    }

    .recommend-title {
        font-family: 'Montserrat', sans-serif;
        color: #7A3C4B;
        font-size: 1.02rem;
        font-weight: 800;
        margin: 14px 0 6px 0;
    }

    .recommend-text {
        font-family: 'Montserrat', sans-serif;
        color: #333;
        font-size: 0.94rem;
        line-height: 1.55;
        margin-bottom: 10px;
    }

    .technical-box {
        background: #F7F2F4;
        border-left: 5px solid #EBA6A6;
        border-radius: 14px;
        padding: 12px 14px;
        margin-top: 10px;
        font-family: 'Montserrat', sans-serif;
        color: #333;
        font-size: 0.92rem;
        line-height: 1.5;
    }

    .mini-label {
        font-weight: 800;
        color: #7A3C4B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def normalize_text(value: str) -> str:
    value = str(value or "").strip().lower()
    value = unicodedata.normalize("NFD", value)
    return "".join(ch for ch in value if unicodedata.category(ch) != "Mn")


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", str(value or ""))


def split_values(value: str) -> list[str]:
    return [p.strip() for p in re.split(r"[;|,]", str(value or "")) if p.strip()]


def contains_choice(cell_value: str, choice: str) -> bool:
    if not choice or choice in {"Todas", "Todos", "Qualquer", "Não sei"}:
        return True
    return normalize_text(choice) in normalize_text(cell_value)


def safe_get(row, column: str, default=""):
    if column not in row.index:
        return default
    value = row[column]
    return value if pd.notna(value) else default


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [
        str(col).replace("\ufeff", "").replace("\xa0", " ").strip()
        for col in df.columns
    ]
    return df


def unique_options(df: pd.DataFrame, column: str, default_label: str) -> list[str]:
    values = []
    if column in df.columns:
        for item in df[column].tolist():
            values.extend(split_values(item))
    clean = sorted({v for v in values if v and normalize_text(v) != "nan"})
    return [default_label] + clean


def convert_google_drive_url(url: str) -> str:
    url = str(url or "").strip()

    if not url or url.lower() == "nan":
        return ""

    if "drive.google.com" in url:
        match = re.search(r"/file/d/([^/]+)", url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1200"

        match = re.search(r"[?&]id=([^&]+)", url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1200"

    return url


@st.cache_data(ttl=120, show_spinner=False)
def read_google_csv(url: str) -> pd.DataFrame:
    response = requests.get(
        url,
        timeout=30,
        allow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "text/csv,text/plain,*/*"},
    )
    response.raise_for_status()

    response_start = response.text.lstrip().lower()[:200]
    if response_start.startswith("<html") or response_start.startswith("<!doctype html"):
        raise ValueError(
            "A planilha não retornou CSV. Verifique se ela está pública para leitura por link."
        )

    df = pd.read_csv(StringIO(response.text), encoding="utf-8-sig")
    return normalize_columns(df).fillna("")


@st.cache_data(ttl=120, show_spinner=False)
def load_data(url: str) -> pd.DataFrame:
    if not SPREADSHEET_ID and "GOOGLE_SHEET_CSV_URL" not in st.secrets:
        raise ValueError("Configure SPREADSHEET_ID nos Secrets do Streamlit.")

    df = read_google_csv(url)

    required = [
        "ativo",
        "nome_look",
        "ocasiao",
        "estilo_desejado",
        "formato_rosto",
        "tipo_cabelo",
        "comprimento_cabelo",
        "cabelo_recomendado",
        "maquiagem_recomendada",
        "sobrancelha_recomendada",
        "unha_recomendada",
        "score_base",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes na planilha: {missing}")

    df = df[df["ativo"].astype(str).str.strip().str.casefold().eq("sim")].copy()
    df["score_base"] = pd.to_numeric(df["score_base"], errors="coerce").fillna(0)

    return df.fillna("")


@st.cache_data(ttl=60, show_spinner=False)
def load_clients(url: str) -> pd.DataFrame:
    df = read_google_csv(url)

    required = ["ativo", "nome_cliente", "telefone"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes na aba de clientes: {missing}")

    df["telefone_normalizado"] = df["telefone"].astype(str).apply(normalize_phone)
    df["nome_normalizado"] = df["nome_cliente"].astype(str).apply(normalize_text)

    return df.fillna("")


def is_authorized_client(clientes_df: pd.DataFrame, nome: str, telefone: str) -> bool:
    nome_norm = normalize_text(nome)
    tel_norm = normalize_phone(telefone)

    if not nome_norm or not tel_norm:
        return False

    ativos = clientes_df[
        clientes_df["ativo"].astype(str).str.strip().str.casefold().eq("sim")
    ].copy()

    match_tel = ativos["telefone_normalizado"].eq(tel_norm)
    match_nome = ativos["nome_normalizado"].apply(
        lambda n: nome_norm in n or n in nome_norm
    )

    return bool(ativos[match_tel & match_nome].shape[0] > 0)


def log_access(payload: dict) -> None:
    if not LOG_WEBAPP_URL:
        return

    try:
        requests.post(
            LOG_WEBAPP_URL,
            json=payload,
            timeout=10,
            headers={"User-Agent": "GlowGlam-LIIVV"},
        )
    except Exception:
        pass


def calculate_score(row, filtros: dict) -> float:
    pesos = {
        "ocasiao": 28,
        "estilo_desejado": 24,
        "formato_rosto": 15,
        "tipo_cabelo": 15,
        "comprimento_cabelo": 10,
        "intensidade_maquiagem": 8,
        "foco_maquiagem": 8,
    }

    score = float(safe_get(row, "score_base", 0) or 0) * 0.35

    for coluna, escolha in filtros.items():
        if coluna == "tempo_max_cliente":
            continue
        if escolha in {"Todas", "Todos", "Qualquer", "Não sei"}:
            continue
        if contains_choice(safe_get(row, coluna), escolha):
            score += pesos.get(coluna, 5)

    tempo = filtros.get("tempo_max_cliente")
    if tempo:
        try:
            if float(safe_get(row, "tempo_max", 999)) <= float(tempo):
                score += 18
            else:
                score -= 20
        except Exception:
            pass

    return round(score, 2)


def get_image_url(row) -> str:
    url = (
        str(safe_get(row, "url_imagem_catalogo", "")).strip()
        or str(safe_get(row, "image_url_manual", "")).strip()
        or str(safe_get(row, "url_link_imagem", "")).strip()
    )
    return convert_google_drive_url(url)


def render_image(image_url: str):
    if not image_url:
        st.info("Imagem ainda não cadastrada no catálogo visual.")
        return

    try:
        st.image(image_url, use_container_width=True)
    except Exception:
        st.markdown(
            f"""
            <a href="{image_url}" target="_blank">
                Abrir imagem da recomendação
            </a>
            """,
            unsafe_allow_html=True,
        )


def render_result(row, rank: int):
    image_url = get_image_url(row)

    with st.container():
        st.markdown('<div class="result-card">', unsafe_allow_html=True)

        col_img, col_txt = st.columns([1.05, 1.7], gap="large")

        with col_img:
            render_image(image_url)

        with col_txt:
            st.markdown(
                f"""
                <p class="look-title">{rank}. {safe_get(row, "nome_look")}</p>
                <div class="look-subtitle">Glow Glam Recommendation</div>

                <span class="badge">{safe_get(row, "ocasiao")}</span>
                <span class="badge">{safe_get(row, "estilo_desejado")}</span>
                <span class="badge">{safe_get(row, "tempo_total_estimado")}</span>

                <div class="recommend-title">Cabelo</div>
                <div class="recommend-text">
                    <span class="mini-label">{safe_get(row, "cabelo_recomendado")}</span><br>
                    {safe_get(row, "descricao_cabelo")}
                </div>

                <div class="recommend-title">Maquiagem</div>
                <div class="recommend-text">
                    <span class="mini-label">{safe_get(row, "maquiagem_recomendada")}</span><br>
                    {safe_get(row, "descricao_maquiagem")}
                </div>

                <div class="recommend-title">Complementos recomendados</div>
                <div class="recommend-text">
                    <span class="mini-label">Sobrancelha:</span> {safe_get(row, "sobrancelha_recomendada")}<br>
                    <span class="mini-label">Unha:</span> {safe_get(row, "unha_recomendada")} — {safe_get(row, "cores_unha")}
                </div>

                <div class="technical-box">
                    <span class="mini-label">Base técnica:</span>
                    {safe_get(row, "explicacao_tecnica")}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    """
    <div class="liivv-header">
        <div class="liivv-logo">LIIVV</div>
        <div class="liivv-subtitle">Beauty | Glow Glam</div>
    </div>
    """,
    unsafe_allow_html=True,
)


if not st.session_state.get("cliente_autorizado"):
    st.markdown(
        """
        <div class="intro-card">
            <div class="intro-title">Acesso exclusivo para clientes LIIVV</div>
            <p class="intro-text">
                Informe seu nome e telefone para acessar sua recomendação Glow Glam.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        clientes_df = load_clients(CLIENTS_CSV_URL)
    except Exception as exc:
        st.error("Não foi possível carregar a lista de clientes autorizados.")
        with st.expander("Detalhes técnicos"):
            st.code(str(exc))
        st.stop()

    with st.form("login_cliente"):
        nome_login = st.text_input("Nome")
        telefone_login = st.text_input("Telefone / WhatsApp")
        entrar = st.form_submit_button("Acessar Glow Glam")

    if entrar:
        autorizado = is_authorized_client(clientes_df, nome_login, telefone_login)

        log_access({
            "nome_informado": nome_login,
            "telefone_informado": telefone_login,
            "status_acesso": "autorizado" if autorizado else "negado",
            "acao": "login"
        })

        if autorizado:
            st.session_state["cliente_autorizado"] = True
            st.session_state["nome_cliente"] = nome_login
            st.session_state["telefone_cliente"] = telefone_login
            st.rerun()
        else:
            st.error("Não localizamos seu cadastro. Fale com a recepção da LIIVV para liberar seu acesso.")

    st.stop()


st.markdown(
    f"""
    <div class="intro-card">
        <div class="intro-title">Sua produção para depois do trabalho</div>
        <p class="intro-text">
            Olá, {st.session_state.get("nome_cliente", "cliente")}.
            Responda algumas perguntas e receba uma recomendação completa de cabelo,
            maquiagem, sobrancelha e unha para sua ocasião.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


try:
    with st.spinner("Carregando recomendações Glow Glam..."):
        df = load_data(SHEET_URL)
except Exception as exc:
    st.error("Não foi possível carregar a base Glow Glam.")
    with st.expander("Detalhes técnicos"):
        st.code(str(exc))
    st.stop()

if df.empty:
    st.warning("A base Glow Glam está vazia ou não possui recomendações ativas.")
    st.stop()


with st.container():
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Monte sua recomendação</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        ocasiao = st.selectbox("🌙 Ocasião", unique_options(df, "ocasiao", "Todas"))
    with c2:
        tempo = st.selectbox("⏱️ Tempo disponível", ["Qualquer", 45, 60, 75, 90, 115])
    with c3:
        estilo = st.selectbox("✨ Estilo desejado", unique_options(df, "estilo_desejado", "Todos"))

    c4, c5, c6 = st.columns(3)
    with c4:
        rosto = st.selectbox("💆 Formato do rosto", unique_options(df, "formato_rosto", "Não sei"))
    with c5:
        tipo_cabelo = st.selectbox("💇 Tipo de cabelo", unique_options(df, "tipo_cabelo", "Todos"))
    with c6:
        comprimento = st.selectbox("📏 Comprimento", unique_options(df, "comprimento_cabelo", "Todos"))

    c7, c8 = st.columns(2)
    with c7:
        intensidade = st.selectbox(
            "💄 Intensidade da maquiagem",
            unique_options(df, "intensidade_maquiagem", "Todos"),
        )
    with c8:
        foco = st.selectbox(
            "👁️ Foco da maquiagem",
            unique_options(df, "foco_maquiagem", "Todos"),
        )

    buscar = st.button("Ver minhas recomendações Glow Glam")
    st.markdown("</div>", unsafe_allow_html=True)


filtros = {
    "ocasiao": ocasiao,
    "estilo_desejado": estilo,
    "formato_rosto": rosto,
    "tipo_cabelo": tipo_cabelo,
    "comprimento_cabelo": comprimento,
    "intensidade_maquiagem": intensidade,
    "foco_maquiagem": foco,
    "tempo_max_cliente": None if tempo == "Qualquer" else tempo,
}

base = df.copy()
base["score_app"] = base.apply(lambda row: calculate_score(row, filtros), axis=1)

resultado = (
    base.sort_values(by=["score_app", "score_base"], ascending=[False, False])
    .head(3)
)

if buscar:
    log_access({
        "nome_informado": st.session_state.get("nome_cliente", ""),
        "telefone_informado": st.session_state.get("telefone_cliente", ""),
        "status_acesso": "autorizado",
        "acao": "recomendacao",
        "ocasiao": ocasiao,
        "tempo": tempo,
        "estilo": estilo,
        "formato_rosto": rosto,
        "tipo_cabelo": tipo_cabelo,
        "comprimento": comprimento,
        "intensidade_maquiagem": intensidade,
        "foco_maquiagem": foco,
        "resultado_1": safe_get(resultado.iloc[0], "nome_look", "") if len(resultado) > 0 else "",
        "resultado_2": safe_get(resultado.iloc[1], "nome_look", "") if len(resultado) > 1 else "",
        "resultado_3": safe_get(resultado.iloc[2], "nome_look", "") if len(resultado) > 2 else "",
    })

    st.markdown('<div class="section-title">Suas recomendações</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="section-title">Sugestões em destaque</div>', unsafe_allow_html=True)

for rank, (_, row) in enumerate(resultado.iterrows(), start=1):
    render_result(row, rank)
