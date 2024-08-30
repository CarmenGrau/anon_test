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
      
        user_input_reference = st.text_area("Add your references (if any) here:", height=200, max_chars=2000)

        user_input = st.text_area("Enter the text you want to anonymize here:", height=200, max_chars=9000)
        
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
                    anon_output = st.text_area("Anonymized text:", value=anonymized_text, height=200)
                    

                except json.JSONDecodeError as e:
                    st.error(f"Failed to decode JSON: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
            
            else:
                st.warning("Please enter some text before submitting.")

        else:
            anon_output = st.text_area("Anonymized text:", value="", height=300)
        
        st.markdown('</div>', unsafe_allow_html=True)
   