EVAL_CASES = [
    # --- Casos Originales (1 - 4) ---
    (
        "780.0,FR,22,true,electronics,ES",
        "CARD-4532",
        "Patron de riesgo alto por pais distinto, horario nocturno y compra online.",
    ),
    (
        "2400.0,US,03,true,electronics,ES",
        "CARD-1024",
        "Caso similar a fraude conocido. Bloqueo inmediato.",
    ),
    (
        "3000.0,US,03,true,electronics,ES",
        "CARD-5005",
        "Todos los factores de riesgo alto presentes.",
    ),
    (
        "500.0,FR,22,false,supermarket,ES",
        "CARD-5006",
        "Pais distinto mas horario nocturno.",
    ),

    # --- Casos P5+ (5 - 10) ---
    (
        "320.0,IT,14,false,restaurant,ES",
        "CARD-6101",
        "Operacion presencial en el extranjero cubierta por aviso de viaje vigente.",
    ),
    (
        "4500.0,ES,11,true,business_services,ES",
        "CARD-6102",
        "Monto elevado en pais habitual y horario diurno sin factores de riesgo.",
    ),
    (
        "45.0,ES,02,true,food_delivery,ES",
        "CARD-6103",
        "Operacion nocturna online de bajo importe en el pais de origen.",
    ),
    (
        "19.99,IE,16,true,digital_services,ES",
        "CARD-6104",
        "Compra online internacional de bajo importe en horario habitual.",
    ),
    (
        "150.0,DE,15,false,pharmacy,ES",
        "CARD-9901",
        "Evidencia insuficiente en el contexto recuperado para determinar riesgo.",
    ),
    (
        "890.0,UK,19,true,travel,ES",
        "CARD-0000",
        "Evidencia insuficiente en el contexto recuperado para determinar riesgo.",
    ),

    # --- Ampliación P5.1 (11 - 20) ---
    # 11. Fraude confirmado: electrónica online nocturna desde Asia
    (
        "1950.0,CN,04,true,electronics,ES",
        "CARD-7001",
        "Caso similar a fraude conocido en electronica online nocturna desde pais extranjero. Bloqueo inmediato.",
    ),
    # 12. Fraude confirmado: importe alto + país distinto + madrugada
    (
        "2850.0,BR,01,true,electronics,ES",
        "CARD-7002",
        "Patron de riesgo alto con todos los factores activos. Requiere bloqueo preventivo.",
    ),
    # 13. Sospechosa: electrónica online en país distinto en horario diurno
    (
        "1100.0,PT,13,true,electronics,ES",
        "CARD-7003",
        "Compra online de electronica de importe alto en pais distinto al habitual.",
    ),
    # 14. Sospechosa: importe alto en horario nocturno dentro del país habitual
    (
        "1650.0,ES,03,true,electronics,ES",
        "CARD-7004",
        "Operacion online de electronica de importe alto en horario nocturno dentro del pais habitual.",
    ),
    # 15. Sospechosa: compra presencial nocturna en el extranjero
    (
        "620.0,MX,23,false,jewelry,ES",
        "CARD-7005",
        "Patron de riesgo por transaccion en pais distinto al habitual y horario nocturno.",
    ),
    # 16. Normal: compra diaria habitual en supermercado local
    (
        "68.50,ES,18,false,supermarket,ES",
        "CARD-8001",
        "No hay contexto recuperado. El sistema se abstuvo.",
    ),
    # 17. Normal: suscripción digital recurrente en país habitual
    (
        "12.99,ES,10,true,digital_services,ES",
        "CARD-8002",
        "No hay contexto recuperado. El sistema se abstuvo.",
    ),
    # 18. Normal: combustible presencial en horario laboral
    (
        "55.0,ES,08,false,gas_station,ES",
        "CARD-8003",
        "No hay contexto recuperado. El sistema se abstuvo.",
    ),
    # 19. Abstención: operación presencial de bajo monto en país vecino de día
    (
        "28.0,PT,12,false,cafe,ES",
        "CARD-9902",
        "No hay contexto recuperado. El sistema se abstuvo.",
    ),
    # 20. Abstención: compra online diurna moderada en librería internacional
    (
        "85.0,US,15,true,books,ES",
        "CARD-9903",
        "No hay contexto recuperado. El sistema se abstuvo.",
    ),
]