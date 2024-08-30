import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import json

st.title("Anon playground")

default_system_prompt = """
        Eres un anonimizador experto que enmascara los datos personales del texto para que ningún individuo pueda ser identificado.
        Encuentra todas las entidades sensibles que aparecen en el texto y sustitúyelas por las etiquetas correspondientes. 

        Las etiquetas y sus descripciones son: 
        - <PER>: sustituye a personas. 
        - <LOC>: sustituye ubicaciones.
        - <COUNTRY>: sustituye países.
        - <PHONE>: sustituye números de teléfono. 
        - <EMAIL>: sustituye correos electrónicos.
        - <DAT>: sustituye fechas. 
        - <ORG>: sustituye organizaciones. 
        - <BANK_ACC>: sustituye números que componen cuentas bancarias. 
        - <NAT>: sustituye nacionalidades. 
        - <PROF>: sustituye profesiones. 
        - <ID>: sustituye números de identificación. 
        - <CREDIT_CARD>: sustituye números que componen tarjetas de crédito. 
        - <ADDR>: sustituye direcciones.
        - <NUM>: sustituye los números que no se consideren teléfonos, fechas, cuentas bancarias, números de identificación ni tarjetas de crédito.
        - <TIM>: sustituye las horas.
        - <URL>: sustituye las url.

        Ten en cuenta lo siguiente: 
        - En España el documento nacional de identidad (DNI) y el número de identificación fiscal (NIF) tienen el formato “8 números + letra” y el número de identificación de extranjero (NIE), el formato “letra + 7 números + letra”. 
        - Si hay varias entidades del mismo tipo separadas dentro de la misma frase, sustitúyelas todas. 
        - Si un sintagma nominal como ""encargado de ventas"" representa una entidad, sustituye todo el sintagma por la etiqueta correspondiente. 
        - No crees nuevas etiquetas.
        - Cambia solo las partes relevantes y deja intacto el resto del texto. 
        - La relevancia y precisión en tus respuestas son fundamentales.

        Devuelve tu respuesta en un único formato json y sin ningún comentario previo:
        
        -El texto resultante ya enmascarado con la estructura "anonimizado": string, seguido de una coma ',' y una lista con las etiquetas y todas las entidades encontradas que correspondan a esa etiqueta, con la estructura "etiquetas": [{'<PER>': [string, string, string]}, {'<LOC>': string}, {'<NAT>': [string, string]}]

        Toma como referencia los siguientes ejemplos:
        "Anuncio de formalización de contrato\nNúmero de Expediente PASA/23/25/1079\nPublicado en la Plataforma de Contratación del Sector Público el 09-11-2023\na las 09:20 horas.\n\nContrato Sujeto a regulación armonizada No\nDirectiva de aplicación Directiva 2014/24/EU - sobre Contratación Pública\n\nEntidad Adjudicadora\nConcejalía Delegada del Área Específica de Turismo y Promoción de la Ciudad del Ayuntamiento de Málaga\nTipo de Administración Autoridad local\nActividad Principal 1 - Servicios públicos generales"
        {"anonimizado": "Anuncio de formalización de contrato\nNúmero de Expediente PASA/<NUM>\nPublicado en la Plataforma de Contratación del Sector Público el <DAT>\na las <TIM> horas.\n\nContrato Sujeto a regulación armonizada No\nDirectiva de aplicación Directiva <NUM>EU - sobre Contratación Pública\n\nEntidad Adjudicadora\n<ORG>\nTipo de Administración Autoridad local\nActividad Principal <NUM> - Servicios públicos generales", "etiquetas": [{"<NUM>": ["23/25/1079", "2014/24",  "1"]}, {"<DAT>": "09-11-2023"}, {"<TIM>": "09:20"}, {"<ORG>": "Concejalía Delegada del Área Específica de Turismo y Promoción de la Ciudad del Ayuntamiento de Málaga"}]}

        "JUZGADO DE LO CONTENCIOSO ADMINISTRATIVO Nº5\nDE PONTEVEDRA\nCiudad de la Justicia. Planta 10ª, Pontevedra\nTlf.: 915845856. Fax: 915896745\nNIG: 7854215O2589632124\nProcedimiento: Pieza de Medidas Cautelares 955.4/2006. Negociado: MM\nProcedimiento principal:[ASTPOR[ASNPOR]\nDe: D/ña. PEDRO ROCA MARTÍNEZ\nProcurador/a Sr./a.:\nLetrado/a Sr./a.: JOSE MARÍA CASTILLO PÉREZ \nContra D/ña.: AYUNTAMIENTO DE VIGO\nProcurador/a Sr./a.: MARÍA DOLORES MANRESA CÓRDOBA\nLetrado/a Sr./a.:\n\nAUTO Nº 458/2009\nD./Dña. ANA BLANCA CIFUENTES ROJO\nEn Vigo, a diecisiete de abril de dos mil siete."
        {"anonimizado": "<ORG> Nº<NUM>\nDE <LOC>\n<ADDR>, <LOC>\nTlf.: <PHONE>. Fax: <PHONE>\nNIG: <ID>\nProcedimiento: Pieza de Medidas Cautelares <NUM>. Negociado: MM\nProcedimiento principal:[ASTPOR[ASNPOR]\nDe: D/ña. <PER>\n<PROF> Sr./a.:\n<PROF> Sr./a.: <PER> \nContra D/ña.: <ORG>\n<PROF>/a Sr./a.: <PER>\n<PROF> Sr./a.:\n\nAUTO Nº <NUM>\nD./Dña. <PER>\nEn <LOC>, a <DAT>.", "etiquetas": [{<ORG>: ["JUZGADO DE LO CONTENCIOSO ADMINISTRATIVO", "AYUNTAMIENTO DE VIGO"]}, {"<NUM>": ["5",  "955.4/2006", "458/2009"]}, {"<LOC>": ["PONTEVEDRA", "Pontevedra", "Vigo"]}, {"<ADDR>": "Ciudad de la Justicia. Planta 10ª"}, {"<PHONE>": ["915845856", "915896745"]}, {"<ID>": "7854215O2589632124"}, {"<PER>": ["PEDRO ROCA MARTÍNEZ", "JOSE MARÍA CASTILLO PÉREZ", "MARÍA DOLORES MANRESA CÓRDOBA", "ANA BLANCA CIFUENTES ROJO"]}, {"<PROF>":  ["Procurador/a", "Letrado/a", "Procurador/a", "Letrado/a"]}, {"<DAT>": "diecisiete de abril de dos mil siete"}]}
      
    """

st.markdown("""
    <style>
    .css-1v3fvcr {
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

with st.container():

    col1, col2 = st.columns([100, 60])

    with col1:
        st.markdown('<div class="css-1v3fvcr">', unsafe_allow_html=True)

        system_prompt = st.text_area("System prompt:", value=default_system_prompt, height=200, disabled=False)
      
        user_input_reference = st.text_area("Add your references (if any) here:", height=100, max_chars=2000)

        user_input = st.text_area("Enter the text you want to anonymize here:", height=300, max_chars=9000)
        
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="css-1v3fvcr">', unsafe_allow_html=True)

        if st.button("Anonymize"):
            if user_input:
                endpoint = "http://192.168.100.67:8000/anon_test/process"
                if user_input_reference:
                    data = {'text_to_anonymize': user_input,
                            'reference': user_input_reference}
                    print(f'Reference entered: {user_input_reference}')
                else:
                    data = {'text_to_anonymize': user_input}
 
                response = requests.post(endpoint, json=data)
                
                try:
                    response_json = response.json()
                    anonymized_text = response_json.get("llm_response", "No anonymized text found")
                    print(f'Success! The anonymized text was received!')
                    anon_output = st.text_area("Anonymized text:", value=anonymized_text, height=800)
                    

                except json.JSONDecodeError as e:
                    st.error(f"Failed to decode JSON: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
            
            else:
                st.warning("Please enter some text before submitting.")

        else:
            anon_output = st.text_area("Anonymized text:", value="", height=300)
        
        st.markdown('</div>', unsafe_allow_html=True)
   