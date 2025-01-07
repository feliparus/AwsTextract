import json
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_textract.type_defs import DetectDocumentTextResponseTypeDef

# Nome do arquivo de resposta
RESPONSE_FILE = "analyzeDocResponse.json"


def detect_file_text(file_path: str) -> None:
    """
    Envia uma imagem para o AWS Textract e salva a resposta no arquivo JSON especificado.
    """
    client = boto3.client("textract")

    try:
        with open(file_path, "rb") as f:
            document_bytes = f.read()

        response = client.detect_document_text(Document={"Bytes": document_bytes})

        # Salva a resposta no arquivo JSON com encoding UTF-8
        with open(RESPONSE_FILE, "w", encoding="utf-8") as response_file:
            json.dump(response, response_file, ensure_ascii=False)  # <- permite acentuação correta

        print(f"Resposta salva em {RESPONSE_FILE}")

    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado.")
    except ClientError as e:
        print(f"Erro ao processar o documento: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


def get_lines_from_response() -> list[str]:
    """
    Lê o arquivo de resposta JSON e retorna uma lista de linhas de texto extraídas.
    """
    if not os.path.exists(RESPONSE_FILE):
        print(f"Arquivo {RESPONSE_FILE} não encontrado. Processando a imagem...")
        image_file = str(Path(__file__).parent / "images" / "lista-material-escolar.jpeg")
        detect_file_text(image_file)

    try:
        # Ler o JSON com encoding UTF-8
        with open(RESPONSE_FILE, "r", encoding="utf-8") as f:
            data: DetectDocumentTextResponseTypeDef = json.load(f)
            blocks = data.get("Blocks", [])
            return [block["Text"] for block in blocks if block["BlockType"] == "LINE"]
    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao ler o arquivo de resposta: {e}")
        return []


if __name__ == "__main__":
    # Caminho da imagem
    image_path = str(Path(__file__).parent / "images" / "lista-material-escolar.jpeg")

    # Processar a imagem e exibir as linhas extraídas
    lines = get_lines_from_response()
    if lines:
        print("Linhas extraídas da imagem:")
        for line in lines:
            print(line)
    else:
        print("Nenhum texto foi extraído.")
