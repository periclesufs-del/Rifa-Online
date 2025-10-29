import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Rifa Solidária", layout="centered")

st.title("Rifa Solidária")
st.write("""
Olá, pessoal! Familiares e amigos estão unidos em uma corrente de solidariedade pela saúde da nossa querida amiga Enfermeira Lane. Ela precisa com urgência realizar uma cirurgia de correção de fístula liquórica na coluna torácica, um procedimento essencial para sua recuperação e qualidade de vida.
O custo total é de R$ 106.000,00, valor que inclui honorários médicos (cirurgião, anestesista, neuroestimulação e demais custos hospitalares).
Para ajudar a tornar esse tratamento possível, estamos organizando uma rifa solidária, cuja renda contribuirá de forma significativa para alcançar essa meta. Sua participação faz toda a diferença! Cada gesto de apoio é um passo importante rumo à saúde e ao bem-estar da nossa amiga Lane.
💚
""")

# Exibição dos prêmios
st.markdown("""
### Prêmios:
- 1º Prêmio: Smartphone Samsung A54
- 2º Prêmio: Voucher de R$ 500,00 em loja parceira
- 3º Prêmio: Caixa de som portátil JBL
""")

arquivo_csv = "rifa_participantes.csv"

# Carrega dados existentes e garante presença das colunas corretas
if os.path.exists(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
else:
    df = pd.DataFrame(columns=["Nome", "Contato", "Numero", "Status", "Comprovante"])

# Corrige CSV antigos sem as novas colunas
for col in ["Status", "Comprovante"]:
    if col not in df.columns:
        df[col] = "" if col == "Comprovante" else "pendente"

num_inicial = 1
num_final = 5000
todos_numeros = list(range(num_inicial, num_final+1))

# Bloqueia apenas números não liberados
ocupados = df[df["Status"] != "liberado"]["Numero"].astype(int).tolist() if not df.empty else []
disponiveis = [n for n in todos_numeros if n not in ocupados]

st.subheader("Números disponíveis")
st.write(f"{len(disponiveis)} de {len(todos_numeros)} disponíveis")

# Interface para reserva
numero_escolhido = st.selectbox("Escolha um número disponível:", disponiveis)
nome = st.text_input("Seu nome completo")
contato = st.text_input("Telefone para contato (WhatsApp)")
comprovante = st.file_uploader(
    "Envie seu comprovante de pagamento (opcional, PDF ou imagem)", 
    type=["pdf", "jpg", "jpeg", "png"]
)

if st.button("Reservar número"):
    if nome.strip() == "" or contato.strip() == "":
        st.warning("Preencha todos os campos!")
    elif numero_escolhido in ocupados:
        st.error("Número já reservado. Atualize a página e tente novamente.")
    else:
        # Salva comprovante se enviado
        if comprovante:
            os.makedirs("comprovantes", exist_ok=True)
            ext = os.path.splitext(comprovante.name)[1]
            comp_filename = f"comprovantes/{numero_escolhido}_{nome.strip().replace(' ', '_')}{ext}"
            with open(comp_filename, "wb") as f:
                f.write(comprovante.getbuffer())
            comp_path = comp_filename
        else:
            comp_path = ""
        nova_linha = pd.DataFrame(
            [[nome.strip(), contato.strip(), numero_escolhido, "pendente", comp_path]],
            columns=["Nome", "Contato", "Numero", "Status", "Comprovante"]
        )
        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv(arquivo_csv, index=False)
        st.success(f"Pronto, {nome}! Seu número {numero_escolhido} foi reservado. Status: pendente.")

# Área de gestão apenas para o administrador (protegida por senha simples)
if st.checkbox("Acesso administrativo (organizador)"):
    admin_senha = st.text_input("Digite a senha de administrador:", type="password")
    if admin_senha == "adm123":  # Escolha uma senha forte!
        st.subheader("Gestão de pagamentos e reservas")
        st.dataframe(df)
        numero_gerenciar = st.number_input(
            "Informe o número para liberar/cancelar ou marcar como pago",
            min_value=num_inicial, max_value=num_final, step=1
        )
        acao = st.selectbox("Ação", ["Liberar número (cancelar reserva)", "Marcar como pago"])
        if st.button("Aplicar ação"):
            idx = df[df["Numero"].astype(int) == int(numero_gerenciar)].index
            if len(idx) == 0:
                st.warning("Número não encontrado ou sem reserva ativa.")
            else:
                if acao == "Liberar número (cancelar reserva)":
                    df.loc[idx, "Status"] = "liberado"
                    st.info(f"Número {numero_gerenciar} foi liberado e está disponível novamente.")
                elif acao == "Marcar como pago":
                    df.loc[idx, "Status"] = "pago"
                    st.success(f"Número {numero_gerenciar} foi marcado como pago.")
                df.to_csv(arquivo_csv, index=False)
        if st.button("Exportar lista (CSV)", key="export_admin"):
            df.to_csv(arquivo_csv, index=False)
            st.success("Arquivo atualizado/exportado com sucesso.")
    elif admin_senha != "":
        st.error("Senha incorreta.")


st.info("Ao reservar seu número, confirme pagamento pelo número (97) 984033561. Envie seu comprovante para facilitar a confirmação. Após verificação, seu número será validado!")
