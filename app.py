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

O sorteio será realizado às 18h (Horário de Manaus) do dia 13/12/2025 de forma online pelo link disponibilizado ao efetuar a compra.
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

# Carrega dados existentes
if os.path.exists(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
else:
    df = pd.DataFrame(columns=["Nome", "Contato", "Quantidade", "Valor Total"])

# Garante que as colunas existam
for col in ["Quantidade", "Valor Total"]:
    if col not in df.columns:
        df[col] = 0

st.subheader("Cadastro de Participante")
st.write("Preencha seus dados e escolha quantos números deseja comprar.")

nome = st.text_input("Seu nome completo")
contato = st.text_input("Telefone para contato (WhatsApp)")
quantidade = st.number_input(
    "Quantos números você deseja comprar?",
    min_value=1,
    max_value=100,
    value=1,
    step=1
)

# Calcula valor total
valor_unitario = 5.00
valor_total = quantidade * valor_unitario

st.info(f"Valor total a pagar: **R$ {valor_total:.2f}**")

if st.button("Cadastrar"):
    if nome.strip() == "" or contato.strip() == "":
        st.warning("Preencha todos os campos!")
    else:
        nova_linha = pd.DataFrame(
            [[nome.strip(), contato.strip(), quantidade, valor_total]],
            columns=["Nome", "Contato", "Quantidade", "Valor Total"]
        )
        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv(arquivo_csv, index=False)
        
        st.success(f"Cadastro de {nome} realizado com sucesso!")
        st.success(f"Você está concorrendo com **{quantidade} número(s)**!")
        st.markdown("**Chave Pix para pagamento: Iracilane Vale Alves (CAIXA)**")
        st.code("17981539431", language='text')
        st.markdown(f"**Valor a pagar via Pix: R$ {valor_total:.2f}**")
        st.info("Após o pagamento, você estará automaticamente concorrendo no sorteio.")
        st.markdown("**Link para assistir o sorteio (13/12/2025 às 18h):**")
        st.code("https://meet.google.com/fed-asyo-pdf", language='text')

# Área de gestão administrativa por senha (apenas visualização e exportação)
if st.checkbox("Acesso administrativo (organizador)"):
    admin_senha = st.text_input("Digite a senha de administrador:", type="password")
    if admin_senha == "142758Ufal!@#":
        st.subheader("Lista de Participantes Cadastrados")
        st.dataframe(df)
        
        # Estatísticas rápidas
        if not df.empty:
            total_participantes = len(df)
            total_numeros = df["Quantidade"].sum()
            total_arrecadado = df["Valor Total"].sum()
            st.metric("Total de Participantes", total_participantes)
            st.metric("Total de Números Vendidos", int(total_numeros))
            st.metric("Total Arrecadado (estimado)", f"R$ {total_arrecadado:.2f}")
        
        if st.button("Exportar lista (CSV)", key="export_admin"):
            df.to_csv(arquivo_csv, index=False)
            st.success("Arquivo exportado com sucesso!")
            st.download_button(
                label="Baixar CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='rifa_participantes.csv',
                mime='text/csv',
            )
    elif admin_senha != "":
        st.error("Senha incorreta.")

st.markdown(
    "<span style='color:blue'><b>"
    "A participação será confirmada através do extrato bancário Pix. "
    "Certifique-se de realizar o pagamento com o mesmo nome cadastrado e o valor correto. "
    "Qualquer dúvida entre em contato pelo número (97) 98403 3561."
    "</b></span>",
    unsafe_allow_html=True
)
