
from groq import Groq
from src.core.config import settings

client = Groq(
    api_key=settings.GROQ_API_KEY,
)

def valid_product(product) -> str:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Eres un clasificador estricto que determina si un nombre corresponde a un repuesto, accesorio o servicio válido para un vehículo. Tu respuesta DEBE SER ÚNICAMENTE la palabra 'si' o la palabra 'no'. No agregues puntos, mayúsculas, ni ninguna otra explicación."
            },
            {
                "role": "user",
                "content": f"Producto: {product}",
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.0,
    )
    ans = chat_completion.choices[0].message.content.strip().lower()
    
    if ans.endswith('.'):
        ans = ans[:-1]
    return ans


def valid_products(products : list) -> list:
    valid_items = []
    for p in products:
        if valid_product(p["descripcion"]) == "si":
            valid_items.append(p)
    return valid_items