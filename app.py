import sqlite3
import uuid
import smtplib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import streamlit as st

st.set_page_config(page_title="PPGCA/UFAM · Fluxo Discente", layout="wide")

DB_PATH = Path(__file__).parent / "ppgca_fluxo.db"
BASE_URL_HINT = "https://rifa-online-2wluyopwprcysjzdp7zomy.streamlit.app/"

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f7f6f2 0%, #fbfbf8 100%); }
    .ufam-banner { background: linear-gradient(120deg, #004b2d 0%, #0a6b46 50%, #014f86 100%); color: white; padding: 1.2rem 1.4rem; border-radius: 18px; margin-bottom: 1rem; box-shadow: 0 10px 28px rgba(0,0,0,.12); }
    .ufam-grid { display: grid; grid-template-columns: 88px 1fr; gap: 1rem; align-items: center; }
    .ufam-mark { width: 88px; height: 88px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #ffffff 0 10%, #f5d04c 11% 18%, #ffffff 19% 22%, #c2272d 23% 27%, #ffffff 28% 31%, #2f7d32 32% 38%, #ffffff 39% 42%, #0d5ea8 43% 49%, #ffffff 50% 53%, #004b2d 54% 60%, #ffffff 61% 100%); border: 4px solid rgba(255,255,255,.24); }
    .ufam-title { font-size: 2rem; font-weight: 700; margin-bottom: .25rem; }
    .ufam-subtitle { font-size: 1rem; opacity: .96; }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            status TEXT NOT NULL,
            aluno_nome TEXT,
            aluno_email TEXT,
            orientador_nome TEXT,
            orientador_email TEXT,
            linha_pesquisa TEXT,
            semestre TEXT,
            fase_curso TEXT,
            bolsa TEXT,
            metas_previstas TEXT,
            produtos_previstos TEXT,
            dificuldades TEXT,
            parecer_orientador TEXT,
            observacoes_orientador TEXT,
            metas_cumpridas TEXT,
            pendencias TEXT,
            proximos_passos TEXT,
            resumo_previsto TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_submission(data):
    conn = get_conn()
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """
        INSERT INTO submissions (
            id, tipo, created_at, updated_at, status, aluno_nome, aluno_email,
            orientador_nome, orientador_email, linha_pesquisa, semestre,
            fase_curso, bolsa, metas_previstas, produtos_previstos, dificuldades,
            parecer_orientador, observacoes_orientador, metas_cumpridas,
            pendencias, proximos_passos, resumo_previsto
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["id"], data["tipo"], now, now, data["status"], data.get("aluno_nome"), data.get("aluno_email"),
            data.get("orientador_nome"), data.get("orientador_email"), data.get("linha_pesquisa"), data.get("semestre"),
            data.get("fase_curso"), data.get("bolsa"), data.get("metas_previstas"), data.get("produtos_previstos"), data.get("dificuldades"),
            data.get("parecer_orientador"), data.get("observacoes_orientador"), data.get("metas_cumpridas"),
            data.get("pendencias"), data.get("proximos_passos"), data.get("resumo_previsto")
        )
    )
    conn.commit()
    conn.close()


def update_approval(submission_id, parecer, observacoes):
    conn = get_conn()
    now = datetime.now().isoformat(timespec="seconds")
    status_map = {
        "Homologado": "homologado",
        "Homologado com ressalvas": "homologado_com_ressalvas",
        "Devolver para ajustes": "devolvido_para_ajustes",
    }
    conn.execute(
        "UPDATE submissions SET parecer_orientador = ?, observacoes_orientador = ?, status = ?, updated_at = ? WHERE id = ?",
        (parecer, observacoes, status_map.get(parecer, "pendente_orientador"), now, submission_id),
    )
    conn.commit()
    conn.close()


def get_submission(submission_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
    conn.close()
    return row


def get_all_submissions():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM submissions ORDER BY created_at DESC", conn)
    conn.close()
    return df


def make_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def build_link(submission_id, role):
    params = urlencode({"view": role, "id": submission_id})
    return f"{BASE_URL_HINT}?{params}"


def status_badge(status):
    colors = {
        "pendente_orientador": ("#8a5300", "#fff4df"),
        "homologado": ("#1e6a33", "#eaf7ee"),
        "homologado_com_ressalvas": ("#7a5a00", "#fff6d8"),
        "devolvido_para_ajustes": ("#8f1f44", "#fdebf2"),
    }
    fg, bg = colors.get(status, ("#444", "#f1f1f1"))
    return f"<span style='padding:.35rem .6rem;border-radius:999px;background:{bg};color:{fg};font-size:.85rem;font-weight:600'>{status.replace('_',' ')}</span>"


def get_email_config():
    return st.secrets["email"] if "email" in st.secrets else None


def send_email(to_email, subject, plain_body, html_body):
    email_cfg = get_email_config()
    if not email_cfg:
        return False, "Configuração de e-mail não encontrada em st.secrets."
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_cfg["sender_email"]
    msg["To"] = to_email
    msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        if int(email_cfg["port"]) == 465:
            with smtplib.SMTP_SSL(email_cfg["host"], int(email_cfg["port"])) as server:
                server.login(email_cfg["username"], email_cfg["password"])
                server.sendmail(email_cfg["sender_email"], [to_email], msg.as_string())
        else:
            with smtplib.SMTP(email_cfg["host"], int(email_cfg["port"])) as server:
                server.starttls()
                server.login(email_cfg["username"], email_cfg["password"])
                server.sendmail(email_cfg["sender_email"], [to_email], msg.as_string())
        return True, "ok"
    except Exception as e:
        return False, str(e)


def send_approval_email(to_email, orientador_nome, aluno_nome, submission_id, tipo):
    approval_link = build_link(submission_id, "orientador")
    subject = f"PPGCA/UFAM - Solicitação de chancela de {tipo}"
    plain_body = f"Prezado(a) Prof.(a) {orientador_nome},\n\nInformamos que o(a) discente {aluno_nome} submeteu o documento referente a {tipo}.\n\nLink para chancela:\n{approval_link}\n\nProtocolo: {submission_id}\n\nAtenciosamente,\nCoordenação do PPGCA/UFAM"
    html_body = f"<html><body><p>Prezado(a) Prof.(a) <strong>{orientador_nome}</strong>,</p><p>Informamos que o(a) discente <strong>{aluno_nome}</strong> submeteu o documento referente a <strong>{tipo}</strong>.</p><p><a href='{approval_link}'>Acessar documento para chancela</a></p><p><strong>Protocolo:</strong> {submission_id}</p><p>Atenciosamente,<br><strong>Coordenação do PPGCA/UFAM</strong></p></body></html>"
    success, result = send_email(to_email, subject, plain_body, html_body)
    return success, approval_link if success else result


def send_student_submission_email(to_email, aluno_nome, submission_id, tipo, orientador_nome):
    subject = f"PPGCA/UFAM - Confirmação de submissão de {tipo}"
    plain_body = f"Prezado(a) {aluno_nome},\n\nSua submissão referente a {tipo} foi registrada e encaminhada ao(à) orientador(a) {orientador_nome}.\n\nProtocolo: {submission_id}\n\nAtenciosamente,\nCoordenação do PPGCA/UFAM"
    html_body = f"<html><body><p>Prezado(a) <strong>{aluno_nome}</strong>,</p><p>Sua submissão referente a <strong>{tipo}</strong> foi registrada e encaminhada ao(à) orientador(a) <strong>{orientador_nome}</strong>.</p><p><strong>Protocolo:</strong> {submission_id}</p><p>Atenciosamente,<br><strong>Coordenação do PPGCA/UFAM</strong></p></body></html>"
    return send_email(to_email, subject, plain_body, html_body)


def send_student_decision_email(to_email, aluno_nome, submission_id, tipo, parecer, observacoes):
    subject = f"PPGCA/UFAM - Resultado da chancela de {tipo}"
    obs_text = observacoes if observacoes else "Não foram registradas observações adicionais."
    plain_body = f"Prezado(a) {aluno_nome},\n\nO(A) orientador(a) registrou a seguinte manifestação sobre o documento referente a {tipo}: {parecer}.\n\nProtocolo: {submission_id}\nObservações: {obs_text}\n\nAtenciosamente,\nCoordenação do PPGCA/UFAM"
    html_body = f"<html><body><p>Prezado(a) <strong>{aluno_nome}</strong>,</p><p>O(A) orientador(a) registrou a seguinte manifestação sobre o documento referente a <strong>{tipo}</strong>: <strong>{parecer}</strong>.</p><p><strong>Protocolo:</strong> {submission_id}</p><p><strong>Observações:</strong> {obs_text}</p><p>Atenciosamente,<br><strong>Coordenação do PPGCA/UFAM</strong></p></body></html>"
    return send_email(to_email, subject, plain_body, html_body)


init_db()
query = st.query_params
view = query.get("view", "app")
submission_id = query.get("id", "")

st.markdown(
    "<div class='ufam-banner'><div class='ufam-grid'><div class='ufam-mark'></div><div><div class='ufam-title'>PPGCA/UFAM · Fluxo de acompanhamento discente</div><div class='ufam-subtitle'>Programa de Pós-Graduação em Ciências Ambientais · Universidade Federal do Amazonas</div></div></div></div>",
    unsafe_allow_html=True,
)
st.caption("Ambiente para submissão de plano e relatório semestral, encaminhamento ao orientador e registro formal de chancela.")

with st.sidebar:
    st.markdown("### Configuração do sistema")
    st.text_input("URL base do app", value=BASE_URL_HINT, disabled=True)
    if get_email_config():
        st.success("Configuração de e-mail detectada em st.secrets.")
    else:
        st.warning("Configuração de e-mail ausente. Veja o arquivo secrets-example.toml.")

if view == "orientador" and submission_id:
    registro = get_submission(submission_id)
    if not registro:
        st.error("Registro não encontrado.")
    else:
        st.subheader("Área do orientador")
        st.markdown(f"**Protocolo:** `{registro['id']}`")
        st.markdown(f"**Tipo de documento:** {registro['tipo'].replace('_', ' ').title()}")
        st.markdown(f"**Situação atual:** {status_badge(registro['status'])}", unsafe_allow_html=True)
        st.markdown("### Registro da chancela")
        with st.form("approval_form"):
            parecer = st.selectbox("Manifestação do orientador", ["Homologado", "Homologado com ressalvas", "Devolver para ajustes"])
            obs = st.text_area("Observações do orientador")
            ok = st.form_submit_button("Registrar manifestação")
            if ok:
                update_approval(registro['id'], parecer, obs)
                st.success("Manifestação registrada com sucesso.")
                if registro['aluno_email']:
                    sent_student, student_msg = send_student_decision_email(
                        registro['aluno_email'], registro['aluno_nome'] or 'Discente', registro['id'], registro['tipo'], parecer, obs
                    )
                    if sent_student:
                        st.info("O discente foi notificado por e-mail sobre o resultado da chancela.")
                    else:
                        st.warning(f"A manifestação foi registrada, mas o e-mail ao discente não foi enviado: {student_msg}")
else:
    tab1, tab2, tab3 = st.tabs(["Plano semestral", "Relatório semestral", "Painel da coordenação"])
    with tab1:
        st.subheader("Submissão de plano semestral")
        with st.form("plano_form"):
            c1, c2 = st.columns(2)
            with c1:
                aluno_nome = st.text_input("Nome do discente")
                aluno_email = st.text_input("E-mail do discente")
                linha = st.selectbox("Linha de pesquisa", ["Linha 1", "Linha 2"])
                fase = st.selectbox("Fase do curso", ["Créditos", "Projeto", "Qualificação", "Coleta/Análise", "Redação", "Defesa"])
            with c2:
                orientador_nome = st.text_input("Nome do orientador")
                orientador_email = st.text_input("E-mail do orientador")
                semestre = st.text_input("Semestre de referência", placeholder="Ex.: 2026/1")
                bolsa = st.selectbox("Situação de bolsa", ["Bolsista", "Lista de espera", "Sem bolsa"])
            metas = st.text_area("Metas acadêmicas previstas para o semestre")
            produtos = st.text_area("Produtos acadêmicos previstos")
            dificuldades = st.text_area("Dificuldades previstas ou necessidades de apoio")
            submitted = st.form_submit_button("Submeter plano")
            if submitted:
                sid = make_id("PLN")
                save_submission({
                    "id": sid, "tipo": "plano", "status": "pendente_orientador", "aluno_nome": aluno_nome,
                    "aluno_email": aluno_email, "orientador_nome": orientador_nome, "orientador_email": orientador_email,
                    "linha_pesquisa": linha, "semestre": semestre, "fase_curso": fase, "bolsa": bolsa,
                    "metas_previstas": metas, "produtos_previstos": produtos, "dificuldades": dificuldades
                })
                st.success("Plano submetido com sucesso.")
                success, result = send_approval_email(orientador_email, orientador_nome, aluno_nome, sid, "plano semestral")
                if success:
                    st.success("Mensagem institucional enviada ao orientador para chancela.")
                    st.code(result, language="text")
                else:
                    st.warning("Não foi possível enviar automaticamente a mensagem ao orientador.")
                    st.code(build_link(sid, "orientador"), language="text")
                    st.caption(f"Detalhe técnico: {result}")
                if aluno_email:
                    sent_student, student_msg = send_student_submission_email(aluno_email, aluno_nome, sid, "plano semestral", orientador_nome)
                    if sent_student:
                        st.info("O discente recebeu confirmação de submissão por e-mail.")
                    else:
                        st.warning(f"O plano foi registrado, mas o e-mail ao discente não foi enviado: {student_msg}")
    with tab2:
        st.subheader("Submissão de relatório semestral")
        with st.form("relatorio_form"):
            c1, c2 = st.columns(2)
            with c1:
                aluno_nome = st.text_input("Nome do discente", key="r_aluno_nome")
                aluno_email = st.text_input("E-mail do discente", key="r_aluno_email")
                semestre = st.text_input("Semestre de referência", key="r_semestre", placeholder="Ex.: 2026/1")
            with c2:
                orientador_nome = st.text_input("Nome do orientador", key="r_orientador_nome")
                orientador_email = st.text_input("E-mail do orientador", key="r_orientador_email")
                resumo_previsto = st.text_area("Síntese do que havia sido planejado")
            metas_cumpridas = st.text_area("Metas cumpridas e produção realizada")
            pendencias = st.text_area("Pendências, atrasos ou dificuldades")
            proximos = st.text_area("Encaminhamentos para o semestre seguinte")
            submitted = st.form_submit_button("Submeter relatório")
            if submitted:
                sid = make_id("REL")
                save_submission({
                    "id": sid, "tipo": "relatorio", "status": "pendente_orientador", "aluno_nome": aluno_nome,
                    "aluno_email": aluno_email, "orientador_nome": orientador_nome, "orientador_email": orientador_email,
                    "semestre": semestre, "metas_cumpridas": metas_cumpridas, "pendencias": pendencias,
                    "proximos_passos": proximos, "resumo_previsto": resumo_previsto
                })
                st.success("Relatório submetido com sucesso.")
                success, result = send_approval_email(orientador_email, orientador_nome, aluno_nome, sid, "relatório semestral")
                if success:
                    st.success("Mensagem institucional enviada ao orientador para chancela.")
                    st.code(result, language="text")
                else:
                    st.warning("Não foi possível enviar automaticamente a mensagem ao orientador.")
                    st.code(build_link(sid, "orientador"), language="text")
                    st.caption(f"Detalhe técnico: {result}")
                if aluno_email:
                    sent_student, student_msg = send_student_submission_email(aluno_email, aluno_nome, sid, "relatório semestral", orientador_nome)
                    if sent_student:
                        st.info("O discente recebeu confirmação de submissão por e-mail.")
                    else:
                        st.warning(f"O relatório foi registrado, mas o e-mail ao discente não foi enviado: {student_msg}")
    with tab3:
        st.subheader("Painel da coordenação")
        df = get_all_submissions()
        if df.empty:
            st.info("Nenhuma submissão registrada até o momento.")
        else:
            st.dataframe(
                df[['id','tipo','status','aluno_nome','orientador_nome','orientador_email','semestre','created_at','updated_at']],
                use_container_width=True
            )
            st.download_button(
                "Baixar CSV das submissões",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='ppgca_submissoes.csv',
                mime='text/csv'
            )
