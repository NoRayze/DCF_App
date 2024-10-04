# app.py

import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

# Configurer la page
st.set_page_config(page_title="Analyse Financière d'Entreprises", layout="wide")

# 1. Entrée de la clé API
st.sidebar.header("Configuration")
API_KEY = st.sidebar.text_input("Entrez votre clé API Financial Modeling Prep :", type="password")

if not API_KEY:
    st.warning("Veuillez entrer votre clé API dans la barre latérale pour continuer.")
else:
    # 2. Fonctions de récupération des données avec gestion des erreurs
    @st.cache_data
    def get_company_profile(symbol):
        url = f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={API_KEY}'
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame(data) if data else pd.DataFrame()

    @st.cache_data
    def get_income_statement(symbol):
        url = f'https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=5&apikey={API_KEY}'
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame(data) if data else pd.DataFrame()

    @st.cache_data
    def get_balance_sheet(symbol):
        url = f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?limit=5&apikey={API_KEY}'
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame(data) if data else pd.DataFrame()

    @st.cache_data
    def get_cash_flow(symbol):
        url = f'https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?limit=5&apikey={API_KEY}'
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame(data) if data else pd.DataFrame()

    @st.cache_data
    def get_financial_ratios(symbol):
        url = f'https://financialmodelingprep.com/api/v3/ratios/{symbol}?limit=5&apikey={API_KEY}'
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame(data) if data else pd.DataFrame()

    @st.cache_data
    def get_financial_news(symbol):
        url = f'https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=5&apikey={API_KEY}'
        response = requests.get(url)
        try:
            data = response.json()
        except ValueError:
            st.error("La réponse de l'API n'est pas un JSON valide.")
            return []
        
        # Vérifier si 'data' est une liste
        if isinstance(data, list):
            return data
        else:
            # Gérer le cas où 'data' est un dictionnaire avec un message d'erreur
            error_message = data.get('Error Message', 'Réponse inattendue de l\'API des actualités financières.')
            st.error(f"Erreur de l'API : {error_message}")
            return []

    @st.cache_data
    def get_peers(symbol):
        url = f'https://financialmodelingprep.com/api/v4/company-outlook?symbol={symbol}&apikey={API_KEY}'
        response = requests.get(url)
        data = response.json()
        peers = data.get('profile', {}).get('peersList', [])
        return peers

    @st.cache_data
    def get_ratios_for_companies(symbols):
        ratios = {}
        for sym in symbols:
            df = get_financial_ratios(sym)
            if not df.empty:
                ratios[sym] = df.iloc[0]
        return ratios

    # 3. Interface utilisateur avec Streamlit

    # 3.1. Titre et description
    st.title("Analyse Financière d'Entreprises")
    st.write("""
    Cette application permet d'analyser les données financières des entreprises cotées en bourse.
    """)
    st.write("---")

    # 3.2. Sélection de l'entreprise
    symbol = st.text_input("Entrez le symbole boursier de l'entreprise (ex: AAPL pour Apple):", 'AAPL').upper()

    # 4. Affichage des données et indicateurs financiers
    if symbol:
        try:
            # 4.1. Récupération des données
            profile = get_company_profile(symbol)
            income_statement = get_income_statement(symbol)
            balance_sheet = get_balance_sheet(symbol)
            cash_flow = get_cash_flow(symbol)
            financial_ratios = get_financial_ratios(symbol)
            news = get_financial_news(symbol)
            peers = get_peers(symbol)

            # Vérifier si les données sont disponibles
            if profile.empty or income_statement.empty or balance_sheet.empty or cash_flow.empty:
                st.error("Impossible de récupérer les données financières pour ce symbole. Veuillez vérifier le symbole et votre clé API.")
            else:
                # 4.2. Affichage du profil de l'entreprise
                st.header(f"Profil de l'entreprise : {symbol}")
                st.subheader(profile['companyName'][0])
                st.write(f"**Prix de l'action :** ${profile['price'][0]}")
                st.write(f"**Capitalisation boursière :** {int(profile['mktCap'][0]):,}")
                st.write(f"**Secteur :** {profile['sector'][0]}")
                st.write(f"**Industrie :** {profile['industry'][0]}")
                st.write(f"**Description :** {profile['description'][0]}")
                st.image(profile['image'][0])
                st.write("---")

                # 4.3. Sélection des indicateurs à afficher
                st.header('Sélection des Indicateurs Financiers')
                available_indicators = [
                    'revenue', 'netIncome', 'operatingIncome', 'eps', 'ebitda',
                    'totalAssets', 'totalLiabilities', 'totalStockholdersEquity',
                    'operatingCashFlow', 'capitalExpenditure', 'freeCashFlow'
                ]
                selected_indicators = st.multiselect(
                    "Sélectionnez les indicateurs à afficher :",
                    options=available_indicators,
                    default=['revenue', 'netIncome', 'eps']
                )
                st.write("---")

                # 4.4. Affichage des états financiers avec les indicateurs sélectionnés
                st.header('États Financiers')

                # Convertir la colonne 'date' en datetime
                income_statement['date'] = pd.to_datetime(income_statement['date'])
                balance_sheet['date'] = pd.to_datetime(balance_sheet['date'])
                cash_flow['date'] = pd.to_datetime(cash_flow['date'])

                # Formatage des dates au format jour-mois-année
                income_statement['date_str'] = income_statement['date'].dt.strftime('%d-%m-%Y')
                income_statement.set_index('date_str', inplace=True)

                balance_sheet['date_str'] = balance_sheet['date'].dt.strftime('%d-%m-%Y')
                balance_sheet.set_index('date_str', inplace=True)

                cash_flow['date_str'] = cash_flow['date'].dt.strftime('%d-%m-%Y')
                cash_flow.set_index('date_str', inplace=True)

                # Compte de résultat
                st.subheader('Compte de Résultat')
                st.dataframe(income_statement[[col for col in selected_indicators if col in income_statement.columns]])

                # Bilan
                st.subheader('Bilan')
                st.dataframe(balance_sheet[[col for col in selected_indicators if col in balance_sheet.columns]])

                # Flux de trésorerie
                st.subheader('Flux de Trésorerie')
                st.dataframe(cash_flow[[col for col in selected_indicators if col in cash_flow.columns]])

                st.write("---")

                # 5. Analyse graphique
                st.header('Analyse Graphique')

                # Graphique des indicateurs sélectionnés
                for indicator in selected_indicators:
                    if indicator in income_statement.columns:
                        df = income_statement.reset_index()[['date', indicator]]
                    elif indicator in balance_sheet.columns:
                        df = balance_sheet.reset_index()[['date', indicator]]
                    elif indicator in cash_flow.columns:
                        df = cash_flow.reset_index()[['date', indicator]]
                    else:
                        continue

                    # Formatage des dates
                    df['date'] = pd.to_datetime(df['date'])
                    df['date_str'] = df['date'].dt.strftime('%d-%m-%Y')

                    fig = px.line(df, x='date', y=indicator, title=f'Évolution de {indicator}')
                    fig.update_layout(
                        xaxis_title='Date',
                        xaxis=dict(
                            tickformat='%d-%m-%Y'
                        )
                    )
                    st.plotly_chart(fig)

                st.write("---")

                # 6. Prévision des flux de trésorerie futurs
                st.header('Prévisions Financières Avancées')

                # Sélection du modèle de prévision
                forecast_model = st.selectbox(
                    "Sélectionnez le modèle de prévision :",
                    options=['Croissance Moyenne', 'Régression Linéaire']
                )

                # Prévision en fonction du modèle choisi
                forecast_years = st.slider("Nombre d'années à prévoir", 1, 10, 5)
                last_revenue = income_statement.iloc[0]['revenue']

                if forecast_model == 'Croissance Moyenne':
                    # Estimation du taux de croissance
                    historical_growth_rate = income_statement.sort_values(by='date')['revenue'].pct_change().mean()
                    st.write(f"**Taux de croissance annuel moyen des revenus :** {historical_growth_rate:.2%}")

                    future_revenues = [last_revenue * ((1 + historical_growth_rate) ** i) for i in range(1, forecast_years + 1)]
                    future_dates = pd.date_range(start=income_statement['date'].max() + pd.DateOffset(years=1), periods=forecast_years, freq='Y')
                else:
                    # Régression linéaire
                    from sklearn.linear_model import LinearRegression

                    income_statement_sorted = income_statement.sort_values(by='date')
                    X = income_statement_sorted['date'].map(pd.Timestamp.toordinal).values.reshape(-1, 1)
                    y = income_statement_sorted['revenue'].values

                    model = LinearRegression()
                    model.fit(X, y)

                    future_dates = pd.date_range(start=income_statement_sorted['date'].max() + pd.DateOffset(years=1), periods=forecast_years, freq='Y')
                    X_future = future_dates.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
                    future_revenues = model.predict(X_future)

                future_years = pd.DataFrame({
                    'Date': future_dates,
                    'Revenus Prévisionnels': future_revenues
                })

                # Formatage des dates
                future_years['Date'] = future_years['Date'].dt.strftime('%d-%m-%Y')
                future_years.set_index('Date', inplace=True)

                st.subheader('Prévisions des Revenus')
                st.dataframe(future_years)

                fig = px.line(future_years.reset_index(), x='Date', y='Revenus Prévisionnels', title='Prévision des Revenus')
                fig.update_layout(
                    xaxis_title='Date',
                    xaxis=dict(
                        tickformat='%d-%m-%Y'
                    )
                )
                st.plotly_chart(fig)

                st.write("---")

                # 7. Recommandations et insights
                st.header('Analyse des Ratios Clés')

                if not financial_ratios.empty:
                    latest_ratios = financial_ratios.iloc[0]
                    st.write(f"**Current Ratio:** {latest_ratios['currentRatio']:.2f}")
                    st.write(f"**Quick Ratio:** {latest_ratios['quickRatio']:.2f}")
                    st.write(f"**Debt to Equity Ratio:** {latest_ratios['debtEquityRatio']:.2f}")
                    st.write(f"**Return on Equity (ROE):** {latest_ratios['returnOnEquity']:.2%}")
                    st.write(f"**Price to Earnings Ratio (P/E):** {latest_ratios['priceEarningsRatio']:.2f}")
                    st.write(f"**Price to Book Ratio (P/B):** {latest_ratios['priceToBookRatio']:.2f}")

                    # Recommandations simples
                    st.subheader('Recommandations')
                    if latest_ratios['priceEarningsRatio'] < 15:
                        st.write("L'action **semble sous-évaluée** sur la base du P/E ratio.")
                    elif latest_ratios['priceEarningsRatio'] > 25:
                        st.write("L'action **pourrait être surévaluée** sur la base du P/E ratio.")
                    else:
                        st.write("L'action est **évaluée de manière équitable** sur la base du P/E ratio.")
                else:
                    st.write("Données des ratios financiers indisponibles pour l'analyse.")

                st.write("---")

                # 8. Comparaison avec les concurrents
                st.header('Comparaison avec les Concurrents')

                if peers:
                    st.write(f"**Principaux concurrents de {symbol} :** {', '.join(peers)}")
                    selected_peers = st.multiselect("Sélectionnez les concurrents à comparer :", options=peers, default=peers[:3])

                    if selected_peers:
                        ratios_peers = get_ratios_for_companies(selected_peers + [symbol])

                        ratios_df = pd.DataFrame(ratios_peers).T[['priceEarningsRatio', 'returnOnEquity', 'debtEquityRatio']]
                        ratios_df.columns = ['P/E Ratio', 'ROE', 'Debt to Equity']
                        st.dataframe(ratios_df)

                        # Graphique comparatif
                        fig = px.bar(ratios_df, barmode='group', title='Comparaison des Ratios Financiers')
                        st.plotly_chart(fig)
                else:
                    st.write("Impossible de récupérer la liste des concurrents.")

                st.write("---")

                # 9. Actualités financières
                st.header('Actualités Financières')

                if news:
                    for article in news:
                        if isinstance(article, dict):
                            st.subheader(article.get('title', 'Titre non disponible'))
                            st.write(f"Date : {article.get('publishedDate', 'Date non disponible')}")
                            st.write(article.get('text', 'Texte non disponible'))
                            st.write(f"[Lien vers l'article]({article.get('url', '#')})")
                            st.write("---")
                        else:
                            st.write("Format d'article inattendu.")
                else:
                    st.write("Aucune actualité disponible.")

        except Exception as e:
            st.error(f"Une erreur s'est produite lors de la récupération des données : {e}")
    else:
        st.write("Veuillez entrer un symbole boursier.")

