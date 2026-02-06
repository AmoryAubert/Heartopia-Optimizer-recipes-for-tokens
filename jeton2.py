import os
import streamlit as st
import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable

# streamlit run d:/Python/.venv2/Scripts/jeton2.py

#my_db.connect(username=st.secrets.db_credentials.username, password=st.secrets.db_credentials.password)

st.set_page_config(page_title="Heartopia Optimizer", layout="centered")

st.title("🍳 Heartopia – Optimisation quotidienne")

st.markdown("### 🧺 Ingrédients disponibles")

col1, col2 = st.columns(2)

with col1:
    oeuf = st.number_input("🥚 Œufs", 0, 200, 50)
    sucre = st.number_input("🍬 Sucre glace", 0, 200, 50)
    beurre = st.number_input("🧈 Beurre", 0, 200, 50)

with col2:
    lait = st.number_input("🥛 Lait", 0, 200, 50)
    cafe = st.number_input("☕ Café", 0, 200, 50)
    viande = st.number_input("🥩 Viande", 0, 200, 50)

ingredients_max = {
    "oeuf": oeuf,
    "lait": lait,
    "sucre": sucre,
    "cafe": cafe,
    "beurre": beurre,
    "viande": viande,
}

st.markdown("### ⭐ Bonus hebdomadaire")
bonus_crafts = st.multiselect(
    "⭐ Plats en bonus (x2 cumulables)",
    ["pancake", "cafe_glace", "latte_glace", "veloute", "viande"],
    default=[]
)

BONUS = {k: 1.0 for k in ["pancake", "cafe_glace", "latte_glace", "veloute", "viande"]}

for craft in bonus_crafts:
    BONUS[craft] = 2.0

# --- Optimisation ---
prob = LpProblem("Heartopia", LpMaximize)

pancake = LpVariable("pancake", lowBound=0, cat="Integer")
cafe_glace = LpVariable("cafe_glace", lowBound=0, cat="Integer")
latte_glace = LpVariable("latte_glace", lowBound=0, cat="Integer")
veloute = LpVariable("veloute", lowBound=0, cat="Integer")
viande = LpVariable("viande", lowBound=0, cat="Integer")

prob += (
    pancake * 160 * BONUS["pancake"]
    + cafe_glace * 140 * BONUS["cafe_glace"]
    + latte_glace * 140 * BONUS["latte_glace"]
    + veloute * 160 * BONUS["veloute"]
    + viande * 300 * BONUS["viande"]
)

prob += pancake <= ingredients_max["oeuf"]
prob += pancake + latte_glace * 2 + veloute <= ingredients_max["lait"]
prob += pancake + cafe_glace + latte_glace <= ingredients_max["sucre"]
prob += cafe_glace * 3 + latte_glace <= ingredients_max["cafe"]
prob += veloute + viande <= ingredients_max["beurre"]
prob += viande * 2 <= ingredients_max["viande"]

prob.solve()

# Résultats
crafts = {
    "pancake": int(pancake.varValue),
    "cafe_glace": int(cafe_glace.varValue),
    "latte_glace": int(latte_glace.varValue),
    "veloute": int(veloute.varValue),
    "viande": int(viande.varValue),
}

radis_blanc_utilises = (
    crafts["viande"] * 1
    + crafts["veloute"] * 2
)

st.markdown("### 📋 Crafts optimaux")
st.table(pd.DataFrame.from_dict(crafts, orient="index", columns=["Quantité"]))

# Consommation
used = {
    "oeuf": crafts["pancake"],
    "lait": crafts["pancake"] + 2*crafts["latte_glace"] + crafts["veloute"],
    "sucre": crafts["pancake"] + crafts["cafe_glace"] + crafts["latte_glace"],
    "cafe": 3*crafts["cafe_glace"] + crafts["latte_glace"],
    "beurre": crafts["veloute"] + crafts["viande"],
    "viande": 2*crafts["viande"]
}

df_ing = pd.DataFrame({
    "Utilisé": used,
    "Restant": {k: ingredients_max[k] - used[k] for k in used}
})

st.markdown("### 🥕 Ingrédients – utilisé vs restant")
st.bar_chart(df_ing)

st.markdown("### 🥬 Radis Blancs")
st.metric(
    label="Radis blanc nécessaire",
    value=radis_blanc_utilises
)

st.success(f"🏆 Points totaux : {int(prob.objective.value())}")

if bonus_crafts:
    st.info("⭐ Bonus actifs : " + ", ".join(bonus_crafts))
else:
    st.info("Aucun bonus actif")
