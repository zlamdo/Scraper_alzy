from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import json
from functools import wraps
import base64
import io
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "tajny_klic" 


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Pro přístup k této stránce se musíte přihlásit.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def nacti_produkty():
    produkty = []
    with open("produkty_hierarchie.txt", "r", encoding="utf-8") as file:
        obsah = file.readlines()

    produkt = {}
    for line in obsah:
        line = line.strip()

        if line.startswith("Název:"):
            if produkt:
                produkty.append(produkt)
            produkt = {"Nazev": line.replace("Název:", "").strip()}

        elif line.startswith("Cena (Kč):"):
            produkt["Cena (Kč)"] = int(line.replace("Cena (Kč):", "").strip())

        elif line.startswith("Hodnocení:"):
            produkt["Hodnoceni"] = float(line.replace("Hodnocení:", "").strip())

        elif line.startswith("Dostupnost:"):
            produkt["Dostupnost"] = line.replace("Dostupnost:", "").strip()

        elif line.startswith("Čas:"):
            produkt["Cas"] = line.replace("Čas:", "").strip()
        
        elif line.startswith("URL:"):
            produkt["URL"] = line.replace("URL:", "").strip()

    if produkt:
        produkty.append(produkt)

    return produkty


def najit_produkt(hledany_nazev, cena_od, cena_do, hodnoceni_od, datum_od, sort_order):
    produkty = nacti_produkty()
    vysledky = []

    for produkt in produkty:
        if hledany_nazev and hledany_nazev.lower() not in produkt["Nazev"].lower():
            continue
        if cena_od and int(produkt["Cena (Kč)"]) < int(cena_od):
            continue
        if cena_do and int(produkt["Cena (Kč)"]) > int(cena_do):
            continue
        if hodnoceni_od and produkt["Hodnoceni"] < float(hodnoceni_od):
            continue
        if datum_od and produkt["Cas"] < datum_od:
            continue
        vysledky.append(produkt)

    if sort_order == "asc":
        vysledky.sort(key=lambda x: x["Cena (Kč)"])
    elif sort_order == "desc":
        vysledky.sort(key=lambda x: x["Cena (Kč)"], reverse=True)
    elif sort_order == "rating_desc":
        vysledky.sort(key=lambda x: x["Hodnoceni"], reverse=True)
    elif sort_order == "rating_asc":
        vysledky.sort(key=lambda x: x["Hodnoceni"])
    elif sort_order == "date_asc":
        vysledky.sort(key=lambda x: x["Cas"])
    elif sort_order == "date_desc":
        vysledky.sort(key=lambda x: x["Cas"], reverse=True)

    return vysledky

def nacti_kategorie_urls():
    if not os.path.exists("kategorie_urls.json"):
        return {}
    with open("kategorie_urls.json", "r", encoding="utf-8") as file:
        return json.load(file)

def uloz_kategorie_urls(data):
    with open("kategorie_urls.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def ulozit_uzivatele(username, password):
    with open("users.txt", "a", encoding="utf-8") as file:
        file.write(f"{username},{password}\n")

def overit_uzivatele(username, password):
    if os.path.exists("users.txt"):
        with open("users.txt", "r", encoding="utf-8") as file:
            users = file.readlines()
            for user in users:
                stored_username, stored_password = user.strip().split(',')
                if stored_username == username and stored_password == password:
                    return True
    return False

@app.route("/", methods=["GET", "POST"])
def index():
    if 'username' in session:
        return redirect(url_for('search'))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username and password:
            ulozit_uzivatele(username, password)
            flash("Registrace probíhla úspěšně!", "success")
            return redirect(url_for("login"))
        else:
            flash("Chybí uživatelské jméno nebo heslo", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if overit_uzivatele(username, password):
            session['username'] = username
            flash("Přihlášení probíhlo úspěšně!", "success")
            return redirect(url_for("search"))
        else:
            flash("Chybné uživatelské jméno nebo heslo.", "error")
    return render_template("login.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    search_results = nacti_produkty()
    data = nacti_kategorie_urls()  
    
    if request.method == "POST":
        if "hledany_nazev" in request.form:
            hledany_nazev = request.form.get("hledany_nazev", "")
            cena_od = request.form.get("cena_od", "")
            cena_do = request.form.get("cena_do", "")
            sort_order = request.form.get("sort_order", "asc")
            hodnoceni_od=request.form.get("hodnoceni_od","")
            datum_od=request.form.get("datum_od","")
            search_results = najit_produkt(hledany_nazev, cena_od, cena_do,hodnoceni_od,datum_od, sort_order)
        
        elif "kategorie" in request.form:
            kategorie = request.form.get("kategorie")
            url = request.form.get("url")
            produkt = request.form.get("produkt")

            if not (kategorie and url and produkt):
                flash("Všechna pole jsou povinná!", "error")
            elif not url.startswith("https://www.alza.cz/"):
                flash("URL musí začínat 'https://www.alza.cz/'", "error")
            else:
                if kategorie not in data:
                    data[kategorie] = {}
                data[kategorie][produkt] = url
                uloz_kategorie_urls(data)
                flash("URL byla úspěšně přidána!", "success")

    return render_template("search.html", search_results=search_results, kategorie=data.keys())



@app.route("/add_url", methods=["GET", "POST"])
@login_required
def add_url():
    data = nacti_kategorie_urls()
    if request.method == "POST":
        kategorie = request.form.get("kategorie")
        url = request.form.get("url")
        produkt = request.form.get("produkt")

        if not (kategorie and url and produkt):
            flash("Všechna pole jsou povinná!", "error")
            return redirect(url_for("add_url"))

        if not url.startswith("https://www.alza.cz/"):
            flash("URL musí začínat 'https://www.alza.cz/'", "error")
            return redirect(url_for("add_url"))

        if kategorie not in data:
            data[kategorie] = {}
        data[kategorie][produkt] = url
        uloz_kategorie_urls(data)

        flash("URL byla úspěšně přidána!", "success")
        return redirect(url_for("add_url"))

    return render_template("add_url.html", kategorie=data.keys())

@app.route("/vyvoj_ceny/<nazev>")
@login_required
def vyvoj_ceny(nazev):
    produkty = nacti_produkty()
    produkt_data = [p for p in produkty if p["Nazev"] == nazev]
    if not produkt_data:
        flash("Produkt nebyl nalezen.", "error")
        return redirect(url_for("search"))

    casy = [item["Cas"] for item in produkt_data]
    ceny = [item["Cena (Kč)"] for item in produkt_data]
    plt.figure(figsize=(15, 5))
    plt.plot(casy, ceny, marker='o')
    plt.xlabel('Datum')
    plt.ylabel('Cena (Kč)')
    plt.title(f'Vývoj ceny: {nazev}')
    plt.grid(True)
    plt.xticks(rotation=45,fontsize=8)
    plt.subplots_adjust(bottom=0.28)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template("vyvoj_ceny.html", plot_url=plot_url, nazev=nazev)

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash("Byl(a) jste úspěšně odhlášen(a).", "success")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
