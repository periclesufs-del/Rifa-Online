import streamlit as st
import pandas as pd
import os
from pathlib import Path

st.set_page_config(page_title="Rifa Solidária", layout="centered")

st.title("Rifa Solidária")
st.write("""
Olá, pessoal! Familiares e amigos estão unidos em uma corrente de solidariedade pela saúde da nossa querida amiga Enfermeira Lane. Ela precisa com urgência realizar uma cirurgia de correção de fístula liquórica na coluna torácica, um procedimento essencial para sua recuperação e qualidade de vida.
O custo total é de R$ 106.000,00, valor que inclui honorários médicos (cirurgião, anestesista, neuroestimulação e demais custos hospitalares).
Para ajudar a tornar esse tratamento possível, estamos organizando uma rifa solidária, cuja renda contribuirá de forma significativa para alcançar essa meta. Sua participação faz toda a diferença! Cada gesto de apoio é um passo importante rumo à saúde e ao bem-estar da nossa amiga Lane.
💚

O sorteio será realizado às 18h (Horário de Manaus) do dia 13/12/2025 de forma online pelo link disponibilizado ao efetuar a compra
""")

# Exibição dos prêmios
st.markdown("""
### Prêmios:
- 1º Prêmio: R$ 50,00
- 2º Prêmio: R$ 50,00
- 3º Prêmio: R$ 100,00
- 4º Prêmio: R$ 100,00
- 5º Prêmio: R$ 200,00
- 6º Prêmio: R$ 200,00
- 7º Prêmio: R$ 300,00
- 8º Prêmio: R$ 500,00
""")

# Exibição do valor da rifa
st.markdown("""
### Valor da Rifa:
- Cada número custa: R$ 5,00
""")

arquivo_csv = "rifa_participantes.csv"

# Carrega dados existentes e garante colunas
if os.path.exists(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
else:
    df = pd.DataFrame(columns=["Nome", "Contato", "Status", "Comprovante"])

for col in ["Status", "Comprovante"]:
    if col not in df.columns:
        df[col] = "" if col == "Comprovante" else "pendente"

st.subheader("Cadastro de Participante")
st.write("Preencha seus dados abaixo para participar da rifa.")

nome = st.text_input("Seu nome completo")
contato = st.text_input("Telefone para contato (WhatsApp)")
comprovante = st.file_uploader(
    "Envie seu comprovante de pagamento (opcional, PDF ou imagem)", 
    type=["pdf", "jpg", "jpeg", "png"]
)

if st.button("Cadastrar"):
    if nome.strip() == "" or contato.strip() == "":
        st.warning("Preencha todos os campos!")
    else:
        comp_path = ""
        if comprovante:
            os.makedirs("comprovantes", exist_ok=True)
            ext = os.path.splitext(comprovante.name)[1]
            comp_filename = f"comprovantes/{nome.strip().replace(' ', '_')}{ext}"
            with open(comp_filename, "wb") as f:
                f.write(comprovante.getbuffer())
            comp_path = comp_filename
        
        nova_linha = pd.DataFrame(
            [[nome.strip(), contato.strip(), "pendente", comp_path]],
            columns=["Nome", "Contato", "Status", "Comprovante"]
        )
        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv(arquivo_csv, index=False)
        
        st.success(f"Cadastro de {nome} realizado com sucesso! Status: pendente.")
        st.markdown("**Chave Pix para pagamento: Iracilane Vale Alves (CAIXA)**")
        st.code("17981539431", language='text')
        st.markdown("**Link para assistir o sorteio (13/12/2025 às 18h):**")
        st.code("https://meet.google.com/fed-asyo-pdf", language='text')

# Área de gestão administrativa por senha
if st.checkbox("Acesso administrativo (organizador)"):
    admin_senha = st.text_input("Digite a senha de administrador:", type="password")
    if admin_senha == "142758Ufal!@#":
        st.subheader("Gestão de participantes")
        st.dataframe(df)

        st.subheader("Comprovantes enviados (pendentes)")
        for idx, row in df.iterrows():
            comp = row["Comprovante"]
            if row["Status"] == "pendente" and isinstance(comp, str) and comp.strip():
                comp_path = Path(comp)
                if comp_path.exists():
                    st.markdown(f"**{row['Nome']}** | Contato: {row['Contato']} | Status: {row['Status']}")
                    with open(comp_path, "rb") as f:
                        st.download_button(
                            label=f"Baixar comprovante ({comp_path.name})",
                            data=f,
                            file_name=comp_path.name,
                            mime="application/octet-stream",
                            key=f"download_{comp_path.name}_{idx}"
                        )
                    st.markdown("---")

        # Gerenciamento de status
        st.subheader("Gerenciar Status de Participantes")
        if not df.empty:
            participante_gerenciar = st.selectbox(
                "Selecione o participante",
                options=df.index.tolist(),
                format_func=lambda x: f"{df.loc[x, 'Nome']} - {df.loc[x, 'Contato']} ({df.loc[x, 'Status']})"
            )
            acao = st.selectbox("Ação", ["Marcar como pago", "Cancelar (liberar)"])
            if st.button("Aplicar ação"):
                if acao == "Cancelar (liberar)":
                    df.loc[participante_gerenciar, "Status"] = "liberado"
                    st.info(f"Participante {df.loc[participante_gerenciar, 'Nome']} foi liberado/cancelado.")
                elif acao == "Marcar como pago":
                    df.loc[participante_gerenciar, "Status"] = "pago"
                    st.success(f"Participante {df.loc[participante_gerenciar, 'Nome']} foi marcado como pago.")
                df.to_csv(arquivo_csv, index=False)
        else:
            st.info("Nenhum participante cadastrado ainda.")

        if st.button("Exportar lista (CSV)", key="export_admin"):
            df.to_csv(arquivo_csv, index=False)
            st.success("Arquivo atualizado/exportado com sucesso.")
    elif admin_senha != "":
        st.error("Senha incorreta.")

st.markdown(
    "<span style='color:blue'><b>"
    "Ao final do dia será realizada a atualização dos cadastros. "
    "Cadastros com pagamentos não confirmados serão cancelados. "
    "Qualquer dúvida entre em contato com o administrador da plataforma pelo número (97) 98403 3561."
    "</b></span>",
    unsafe_allow_html=True
)
