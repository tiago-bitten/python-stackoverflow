from flask import Flask, jsonify, render_template, request
import requests
import time

app = Flask(__name__)

QUESTIONS_PER_PAGE = 100
TOTAL_QUESTIONS = 1000
PAGES_TO_FETCH = TOTAL_QUESTIONS // QUESTIONS_PER_PAGE

AVAILABLE_LANGUAGES = ["python", "java", "javascript", "php", "c#", "ruby", "other"]

@app.route('/')
def index():
    return render_template('index.html', languages=AVAILABLE_LANGUAGES)

@app.route('/api/stackoverflow-stats', methods=['POST'])
def get_stackoverflow_stats():
    selected_languages = request.json.get('languages', [])
    if not selected_languages:
        return jsonify({"error": "Nenhuma linguagem selecionada"}), 400

    language_stats = {lang: {"total": 0, "answered": 0} for lang in selected_languages}
    
    try:
        for page in range(1, PAGES_TO_FETCH + 1):
            url = "https://api.stackexchange.com/2.3/questions"
            params = {
                "order": "desc",
                "sort": "activity",
                "intitle": "erro de conexão",
                "site": "pt.stackoverflow",
                "pagesize": QUESTIONS_PER_PAGE,
                "page": page
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            questions = data.get("items", [])

            # Processa perguntas
            for q in questions:
                tags = q.get("tags", [])
                is_answered = q.get("is_answered", False)
                linguagem = tags[0] if tags else "other"

                # Considera apenas linguagens selecionadas
                if linguagem in selected_languages:
                    language_stats[linguagem]["total"] += 1
                    if is_answered:
                        language_stats[linguagem]["answered"] += 1

            time.sleep(1.5)  # Evitar limite da API

        result = [
            {
                "linguagem": lang,
                "total_ocorrencia": stats["total"],
                "taxa_resposta": round((stats["answered"] / stats["total"] * 100), 2) if stats["total"] > 0 else 0.0
            }
            for lang, stats in language_stats.items()
        ]

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Falha ao processar: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)