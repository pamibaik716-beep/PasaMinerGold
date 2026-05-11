# =========================
# PASAMINER GOLD PREMIUM
# Adsterra Ready Version
# =========================

from flask import Flask, render_template_string, request, redirect, session
from pymongo import MongoClient
import random
import time

app = Flask(__name__)

app.secret_key = "CHANGE_THIS_SECRET"

# =========================
# MONGODB
# GANTI URL MONGO
# =========================

MONGO_URL = "mongodb://pasaminergold:M12pami*@ac-gpow4zl-shard-00-00.gnxeyyz.mongodb.net:27017,ac-gpow4zl-shard-00-01.gnxeyyz.mongodb.net:27017,ac-gpow4zl-shard-00-02.gnxeyyz.mongodb.net:27017/?ssl=true&replicaSet=atlas-oy6uk4-shard-0&authSource=admin&appName=Cluster0"

client = MongoClient(MONGO_URL)

db = client["pasaminer"]

users = db["users"]

# =========================
# CONFIG
# =========================

LOGO = "https://files.catbox.moe/8m6l6p.png"

# DIRECT LINK ADSTERRA
ADS_LINK = "GANTI_LINK_ADSTERRA"

# SCRIPT SOCIAL BAR ADSTERRA
ADSTERRA_SCRIPT = """
<script type='text/javascript' src='GANTI_SCRIPT_ADSTERRA'></script>
"""

DAILY_REWARD = 100

# =========================
# RANK
# =========================

def get_rank(gold):

    if gold >= 10000:
        return "💎 Diamond"

    if gold >= 5000:
        return "🥇 Gold"

    if gold >= 1000:
        return "🥈 Silver"

    return "🥉 Bronze"

# =========================
# HTML
# =========================

HTML = '''

<!DOCTYPE html>
<html>

<head>

<title>PasaMiner Gold</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>

body{
background:#0f0f0f;
font-family:Arial;
color:white;
padding:15px;
}

.box{
background:#1c1c1c;
padding:20px;
border-radius:20px;
margin-bottom:15px;
box-shadow:0 0 10px rgba(255,215,0,0.1);
}

.logo{
width:120px;
border-radius:50%;
display:block;
margin:auto;
margin-bottom:10px;
}

.title{
text-align:center;
font-size:28px;
font-weight:bold;
color:gold;
}

.sub{
text-align:center;
color:#aaa;
margin-bottom:15px;
}

.stat{
background:#2a2a2a;
padding:12px;
border-radius:12px;
margin-top:8px;
}

button{
width:100%;
padding:14px;
border:none;
border-radius:12px;
background:gold;
font-weight:bold;
margin-top:10px;
cursor:pointer;
}

input{
width:95%;
padding:12px;
border:none;
border-radius:10px;
background:#333;
color:white;
margin-top:10px;
}

.rank{
font-size:20px;
color:gold;
font-weight:bold;
}

.leader{
background:#222;
padding:10px;
border-radius:10px;
margin-top:5px;
}

a{
text-decoration:none;
}

</style>

</head>

<body>

<div class="box">

<img src="{{logo}}" class="logo">

<div class="title">
PasaMiner Gold
</div>

<div class="sub">
Mining Reward Platform
</div>

{% if not user %}

<form method="POST">

<input type="text" name="username" placeholder="Username" required>

<input type="password" name="password" placeholder="Password" required>

<button type="submit">
LOGIN / REGISTER
</button>

</form>

{% else %}

<div class="rank">
{{rank}}
</div>

<div class="stat">
🪙 Gold : {{user.gold}}
</div>

<div class="stat">
💰 Balance : Rp {{user.balance}}
</div>

<div class="stat">
⚡ Power : {{user.power}}
</div>

<div class="stat">
👑 VIP : {{user.vip}}
</div>

<div class="stat">
👥 Referral : {{user.ref_total}}
</div>

<form action="/mine" method="POST">
<button>⛏ Mine Gold</button>
</form>

<form action="/claim" method="POST">
<button>🎁 Claim Reward</button>
</form>

<a href="/watchads">
<button>
📺 Watch Ads
</button>
</a>

<form action="/daily" method="POST">
<button>
📅 Daily Reward
</button>
</form>

<form action="/recharge" method="POST">
<button>
🔋 Recharge Power
</button>
</form>

<form action="/withdraw" method="POST">

<input type="text" name="wallet" placeholder="Dana / OVO / Gopay" required>

<input type="number" name="amount" placeholder="Jumlah Withdraw" required>

<button>
💸 Withdraw
</button>

</form>

<h3>👑 VIP LEVEL</h3>

<a href="/vip/1">
<button>VIP 1</button>
</a>

<a href="/vip/2">
<button>VIP 2</button>
</a>

<a href="/vip/3">
<button>VIP 3</button>
</a>

<h3>👥 Referral</h3>

<input value="{{ref}}" readonly>

<h3>🏆 Leaderboard Referral</h3>

{% for x in top_ref %}

<div class="leader">
{{x.username}} - {{x.ref_total}} Ref
</div>

{% endfor %}

<br>

<a href="/logout">
<button>
Logout
</button>
</a>

{% endif %}

</div>

{{ads_script|safe}}

</body>
</html>

'''

# =========================
# LOGIN / REGISTER
# =========================

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = users.find_one({
            "username": username
        })

        # LOGIN
        if user:

            if user["password"] == password:

                session["user"] = username

                return redirect("/dashboard")

            return "Password salah"

        # REGISTER
        ref = request.args.get("ref")

        users.insert_one({

            "username": username,
            "password": password,

            "gold": 0,
            "balance": 0,

            "power": 100,

            "vip": 0,

            "ref_total": 0,

            "last_daily": 0,

            "last_ads": 0,

            "ref_by": ref

        })

        # BONUS REF
        if ref:

            users.update_one(
                {"username": ref},
                {
                    "$inc":{
                        "balance": 100,
                        "ref_total": 1
                    }
                }
            )

        session["user"] = username

        return redirect("/dashboard")

    return render_template_string(
        HTML,
        user=None,
        logo=LOGO,
        ads_script=ADSTERRA_SCRIPT
    )

# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    user = users.find_one({
        "username": session["user"]
    })

    rank = get_rank(user["gold"])

    ref = request.host_url + "?ref=" + user["username"]

    top_ref = users.find().sort(
        "ref_total",
        -1
    ).limit(10)

    return render_template_string(
        HTML,
        user=user,
        logo=LOGO,
        rank=rank,
        ref=ref,
        top_ref=top_ref,
        ads_script=ADSTERRA_SCRIPT
    )

# =========================
# MINE
# =========================

@app.route("/mine", methods=["POST"])
def mine():

    if "user" not in session:
        return redirect("/")

    user = users.find_one({
        "username": session["user"]
    })

    if user["power"] >= 5:

        gold = random.randint(5,15)

        users.update_one(
            {"username": session["user"]},
            {
                "$inc":{
                    "gold": gold,
                    "power": -5
                }
            }
        )

    return redirect("/dashboard")

# =========================
# CLAIM
# =========================

@app.route("/claim", methods=["POST"])
def claim():

    if "user" not in session:
        return redirect("/")

    users.update_one(
        {"username": session["user"]},
        {
            "$inc":{
                "gold": 25
            }
        }
    )

    return redirect("/dashboard")

# =========================
# WATCH ADS
# =========================

@app.route("/watchads")
def watchads():

    if "user" not in session:
        return redirect("/")

    user = users.find_one({
        "username": session["user"]
    })

    now = time.time()

    # cooldown 60 detik
    if now - user["last_ads"] < 60:

        return "Tunggu sebelum watch ads lagi"

    users.update_one(
        {"username": session["user"]},
        {
            "$inc":{
                "gold": 50
            },
            "$set":{
                "last_ads": now
            }
        }
    )

    return redirect(ADS_LINK)

# =========================
# DAILY
# =========================

@app.route("/daily", methods=["POST"])
def daily():

    if "user" not in session:
        return redirect("/")

    user = users.find_one({
        "username": session["user"]
    })

    now = time.time()

    if now - user["last_daily"] >= 86400:

        users.update_one(
            {"username": session["user"]},
            {
                "$inc":{
                    "gold": DAILY_REWARD
                },
                "$set":{
                    "last_daily": now
                }
            }
        )

    return redirect("/dashboard")

# =========================
# RECHARGE
# =========================

@app.route("/recharge", methods=["POST"])
def recharge():

    if "user" not in session:
        return redirect("/")

    users.update_one(
        {"username": session["user"]},
        {
            "$set":{
                "power":100
            }
        }
    )

    return redirect("/dashboard")

# =========================
# VIP
# =========================

@app.route("/vip/<int:level>")
def vip(level):

    if "user" not in session:
        return redirect("/")

    users.update_one(
        {"username": session["user"]},
        {
            "$set":{
                "vip": level
            }
        }
    )

    return redirect("/dashboard")

# =========================
# WITHDRAW
# =========================

@app.route("/withdraw", methods=["POST"])
def withdraw():

    if "user" not in session:
        return redirect("/")

    amount = int(request.form["amount"])

    wallet = request.form["wallet"]

    user = users.find_one({
        "username": session["user"]
    })

    if amount < 1000:
        return "Minimal WD 1000"

    if user["balance"] < amount:
        return "Balance kurang"

    users.update_one(
        {"username": session["user"]},
        {
            "$inc":{
                "balance": -amount
            }
        }
    )

    print("========== WD ==========")
    print("USER :", user["username"])
    print("AMOUNT :", amount)
    print("WALLET :", wallet)
    print("========================")

    return redirect("/dashboard")

# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =========================
# RUN
# =========================

app.run(
    host="0.0.0.0",
    port=5000,
    debug=True
)