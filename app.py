import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rifa Online", layout="centered")

st.title("Rifa Solidária")
st.write("Olá, pessoal! Familiares e amigos estão unidos em uma corrente de solidariedade pela saúde da nossa querida amiga Enfermeira Lane. Ela precisa com urgência realizar uma cirurgia de correção de fístula liquórica na coluna torácica, um procedimento essencial para sua recuperação e qualidade de vida. O custo total é de R$ 106.000,00, valor que inclui honorários médicos (cirurgião, anestesista, neuroestimulação e demais custos hospitalares). Para ajudar a tornar esse tratamento possível, estamos organizando uma rifa solidária, cuja renda contribuirá de forma significativa para alcançar essa meta. Sua participação faz toda a diferença! Cada gesto de apoio é um passo importante rumo à saúde e ao bem-estar da nossa amiga Lane. 💚")

# Carrega dados existentes (aqui, rodando local)
try:
    df = pd.read_csv("rifa_participantes.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=["Nome", "Contato", "Numero"])

# Parâmetros da rifa
num_inicial = 1
num_final = 5000  # Altere para 5000 conforme necessidade
todos_numeros = list(range(num_inicial, num_final+1))

# Lista de números já comprados
ocupados = df["Numero"].astype(int).tolist()
disponiveis = [n for n in todos_numeros if n not in ocupados]

st.subheader("Números disponíveis")
st.write(f"{len(disponiveis)} de {len(todos_numeros)} disponíveis")

# Interface de escolha do número
numero_escolhido = st.selectbox("Escolha um número disponível:", disponiveis)
nome = st.text_input("Seu nome completo")
contato = st.text_input("Telefone para contato (WhatsApp)")

if st.button("Reservar número"):
    if nome.strip() == "" or contato.strip() == "":
        st.warning("Preencha todos os campos!")
    elif numero_escolhido in ocupados:
        st.error("Número já reservado. Atualize a página e tente novamente.")
    else:
        nova_linha = pd.DataFrame([[nome.strip(), contato.strip(), numero_escolhido]],
                                  columns=["Nome", "Contato", "Numero"])
        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv("rifa_participantes.csv", index=False)
        st.success(f"Pronto, {nome}! Seu número {numero_escolhido} foi reservado.")

# Exibição da lista de participantes (oculta por padrão)
if st.checkbox("Mostrar todos os participantes"):
    st.dataframe(df)

# Exportação dos inscritos
if st.button("Exportar lista (CSV)"):
    df.to_csv("rifa_participantes.csv", index=False)
    st.success("Arquivo atualizado/exportado com sucesso.")

st.info("Ao reservar seu número, confirme pagamento pelo número (97) 984033561.")