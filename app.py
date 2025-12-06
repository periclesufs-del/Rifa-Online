import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime
import time

st.set_page_config(page_title="Rifa Solidária", layout="centered")

# Menu de navegação
pagina = st.sidebar.radio("Navegação", ["Cadastro de Participantes", "Sorteio ao Vivo"])

if pagina == "Cadastro de Participantes":
    st.title("Rifa Solidária")

    st.write("""
    Olá, pessoal! Familiares e amigos estão unidos em uma corrente de solidariedade pela saúde da nossa querida amiga Enfermeira Lane. Ela precisa com urgência realizar uma cirurgia de correção de fístula liquórica na coluna torácica, um procedimento essencial para sua recuperação e qualidade de vida.

    O custo total é de R$ 106.000,00, valor que inclui honorários médicos (cirurgião, anestesista, neuroestimulação e demais custos hospitalares).

    Para ajudar a tornar esse tratamento possível, estamos organizando uma rifa solidária, cuja renda contribuirá de forma significativa para alcançar essa meta. Sua participação faz toda a diferença! Cada gesto de apoio é um passo importante rumo à saúde e ao bem-estar da nossa amiga Lane.

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
    - Cada rifa custa: R$ 5,00
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
    st.write("Preencha seus dados e escolha quantas rifas deseja comprar.")

    nome = st.text_input("Seu nome completo")
    contato = st.text_input("Telefone para contato (WhatsApp)")
    quantidade = st.number_input(
        "Quantas rifas você deseja comprar?",
        min_value=1,
        max_value=100,
        value=1,
        step=1,
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
                columns=["Nome", "Contato", "Quantidade", "Valor Total"],
            )
            df = pd.concat([df, nova_linha], ignore_index=True)
            df.to_csv(arquivo_csv, index=False)

            st.success(f"Cadastro de {nome} realizado com sucesso!")
            st.success(f"Você está concorrendo com **{quantidade} rifa(s)**!")

            st.markdown("**Chave Pix para pagamento: Iracilane Vale Alves (CAIXA)**")
            st.code("17981539431", language="text")
            st.markdown(f"**Valor a pagar via Pix: R$ {valor_total:.2f}**")
            st.info(
                "Após o pagamento, que será confirmado no extrato da conta recebedora, "
                "você estará automaticamente concorrendo no sorteio."
            )
            st.markdown("**Link para assistir o sorteio (13/12/2025 às 18h):**")
            st.code("https://meet.google.com/fed-asyo-pdf", language="text")

    # Área de gestão administrativa por senha
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
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="rifa_participantes.csv",
                    mime="text/csv",
                )
        elif admin_senha != "":
            st.error("Senha incorreta.")

    st.markdown(
        """
        A participação será confirmada através do extrato bancário Pix. 
        Certifique-se de realizar o pagamento com o mesmo nome cadastrado e o valor correto. 
        Qualquer dúvida entre em contato pelo número (97) 98403 3561.
        """,
        unsafe_allow_html=True,
    )

elif pagina == "Sorteio ao Vivo":
    st.title("🎉 SORTEIO AO VIVO - RIFA SOLIDÁRIA")
    st.markdown("### Enfermeira Lane")

    senha_sorteio = st.text_input("Senha do organizador para iniciar sorteio:", type="password")

    if senha_sorteio == "142758Ufal!@#":
        st.success("✓ Acesso autorizado!")

        uploaded_file = st.file_uploader(
            "Envie o arquivo de participantes aptos (.xlsx)", type=["xlsx"]
        )

        if uploaded_file is not None:
            df_aptos = pd.read_excel(uploaded_file)
            st.success(f"✓ Arquivo carregado! Total de linhas: {len(df_aptos)}")

            if "Nome" not in df_aptos.columns:
                st.error("⚠️ O arquivo deve ter uma coluna chamada 'Nome'")
            else:
                # Lista completa de entradas (uma linha = uma rifa)
                participantes = df_aptos["Nome"].dropna().tolist()

                # Contagem de rifas por pessoa (para transparência)
                contagem_rifas = df_aptos["Nome"].value_counts().to_dict()

                st.info(f"📋 Entradas válidas (rifas): {len(participantes)}")
                st.info(f"👥 Pessoas únicas: {len(contagem_rifas)}")

                premios = [
                    ("1º Prêmio", "R$ 50,00"),
                    ("2º Prêmio", "R$ 50,00"),
                    ("3º Prêmio", "R$ 100,00"),
                    ("4º Prêmio", "R$ 100,00"),
                    ("5º Prêmio", "R$ 200,00"),
                    ("6º Prêmio", "R$ 200,00"),
                    ("7º Prêmio", "R$ 300,00"),
                    ("8º Prêmio", "R$ 500,00"),
                ]

                st.markdown("---")
                st.subheader("🎁 Iniciar Sorteio")

                if st.button("🚀 SORTEAR TODOS OS PRÊMIOS", type="primary"):
                    entradas = participantes.copy()
                    random.shuffle(entradas)

                    resultados = []

                    for nome_premio, valor in premios:
                        if not entradas:
                            st.warning("Não há mais rifas para sortear.")
                            break

                        ganhador = random.choice(entradas)
                        qtd_rifas_ganhador = contagem_rifas.get(ganhador, 1)

                        resultados.append(
                            (nome_premio, valor, ganhador, qtd_rifas_ganhador)
                        )

                        st.markdown(f"### 🎁 {nome_premio}: {valor}")
                        with st.spinner("Sorteando..."):
                            time.sleep(4)

                        st.success(
                            f"🏆 **GANHADOR: {ganhador}** "
                            f"(concorrendo com {qtd_rifas_ganhador} rifa(s))"
                        )
                        st.balloons()
                        time.sleep(2)

                    st.markdown("---")
                    st.markdown("## 📊 RESULTADO FINAL")
                    if resultados:
                        resultado_df = pd.DataFrame(
                            resultados,
                            columns=[
                                "Prêmio",
                                "Valor",
                                "Ganhador",
                                "Rifas do ganhador",
                            ],
                        )
                        st.table(resultado_df)

                        resultado_csv = resultado_df.to_csv(index=False).encode(
                            "utf-8"
                        )
                        st.download_button(
                            label="📥 Baixar Resultado (CSV)",
                            data=resultado_csv,
                            file_name=(
                                f"resultado_sorteio_"
                                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                            ),
                            mime="text/csv",
                        )
        else:
            st.info("👆 Envie o arquivo Excel com os participantes aptos para começar")
    elif senha_sorteio != "":
        st.error("Senha incorreta!")
