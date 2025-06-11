from openai import OpenAI
import time

client = OpenAI(api_key="sua_chave_API")


# Estrutura do diagnóstico
sleep_diagnosis = {
    "Bloco 1: Sintomas e Padrão de Sono": {
        "questions": [
            ("Quantas horas você costuma dormir por noite?", lambda x: 3 if int(x) < 6 else 0),
            ("Você vai dormir e acorda em horários diferentes todos os dias? (s/n)", lambda x: 3 if x.lower() == "s" else 0),
            ("Você acorda cansado mesmo depois de uma noite inteira de sono? (s/n)", lambda x: 2 if x.lower() == "s" else 0),
        ]
    },
    "Bloco 2: Hábitos e Substâncias": {
        "questions": [
            ("Você consome cafeína (café, energético, refrigerante)? Com que frequência?", lambda x: 2 if "todo dia" in x.lower() else 1 if "às vezes" in x.lower() else 0),
            ("Você toma algum medicamento que afeta o sono? Informe nome, dosagem e horário.", lambda x: 0),  # Análise feita pelo modelo
            ("Você usa álcool, nicotina ou outras substâncias à noite?", lambda x: 2 if any(p in x.lower() for p in ["sim", "uso"]) else 0),
        ]
    },
    "Bloco 3: Ambiente e Rotina": {
        "questions": [
            ("Seu quarto é silencioso, escuro e confortável? (s/n)", lambda x: 2 if x.lower() == "n" else 0),
            ("Você usa celular, TV ou computador na cama antes de dormir? (s/n)", lambda x: 2 if x.lower() == "s" else 0),
            ("Você tem rotina noturna regular (ex: leitura, banho quente)? Descreva.", lambda x: 0),
        ]
    },
    "Bloco 4: Emoções e Estresse": {
        "questions": [
            ("Você tem ansiedade, estresse ou pensamentos acelerados na hora de dormir? (s/n)", lambda x: 3 if x.lower() == "s" else 0),
            ("Você acorda no meio da noite pensando em coisas do dia ou preocupado? (s/n)", lambda x: 2 if x.lower() == "s" else 0),
        ]
    }
}

def gerar_recomendacao_gpt4o_por_blocos(score, respostas_por_bloco):
    prompt = f"""
    Um usuário completou um diagnóstico de sono e obteve uma pontuação de risco do sono de {score}/60.
    Abaixo estão as respostas organizadas por categorias. Analise cada bloco e gere um plano de regularização do sono altamente personalizado, prático e detalhado.
    Considere higiene do sono, exposição à luz, rotina, alimentação, ansiedade, uso de substâncias, cochilos e ambiente de sono.

    Para cada área, dê sugestões específicas e informe uma estimativa de tempo (em dias) até os primeiros efeitos positivos.

    Respostas do usuário por bloco:
    """

    for bloco, respostas in respostas_por_bloco.items():
        prompt += f"\n\n{bloco}:\n"
        for pergunta, resposta in respostas:
            prompt += f"- {pergunta} {resposta}\n"

    response = client.chat.completions.create(
        model="gpt-4o",  # Ou "gpt-4o-mini" se preferir
        messages=[
            {"role": "system", "content": "Você é um especialista em sono."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()

# Execução
def run_sleep_diagnosis():
    total_score = 0
    respostas_por_bloco = {}

    print("=== Diagnóstico do Sono ===")
    for bloco_nome, bloco in sleep_diagnosis.items():
        print(f"\n--- {bloco_nome} ---")
        respostas_bloco = []
        for pergunta, pontuador in bloco["questions"]:
            resposta = input(f"-> {pergunta} ")
            try:
                score = pontuador(resposta)
                total_score += score
            except Exception:
                score = 0
                print("Resposta inválida. Considerando 0 pontos.")
            respostas_bloco.append((pergunta, resposta))
        respostas_por_bloco[bloco_nome] = respostas_bloco
        time.sleep(0.5)

    print(f"\nPontuação total de risco: {total_score}/60")

    plano = gerar_recomendacao_gpt4o_por_blocos(total_score, respostas_por_bloco)
    print("\n=== Plano de Regularização do Sono ===\n")
    print(plano)

# Iniciar
if __name__ == "__main__":
    run_sleep_diagnosis()
