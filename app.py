from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory storage for ads (simulating a database)
ads = [
    {"id": 1, "title": "سيارة للبيع", "description": "تويوتا كامري 2022 بحالة ممتازة", "price": "80000", "contact": "0500000000"},
    {"id": 2, "title": "شقة للإيجار", "description": "شقة 3 غرف في وسط الرياض", "price": "35000", "contact": "0555555555"}
]

@app.route('/')
def index():
    return render_template('index.html', ads=ads)

@app.route('/add', methods=('GET', 'POST'))
def add_ad():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        contact = request.form['contact']
        
        new_ad = {
            "id": len(ads) + 1,
            "title": title,
            "description": description,
            "price": price,
            "contact": contact
        }
        ads.append(new_ad)
        return redirect(url_for('index'))
        
    return render_template('add_ad.html')

if __name__ == '__main__':
    app.run(debug=True)