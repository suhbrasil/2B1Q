import socket
import matplotlib.pyplot as plt
import tkinter as tk

# Cria um objeto de socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define o endereço IP e a porta para o socket
host = '192.168.1.6'  # Substitua pelo IP do servidor
port = 12346  # A mesma porta usada pelo servidor

# Conecta-se ao servidor
client_socket.connect((host, port))

# Função para criar o gráfico
def create_graph(data):
    tuple_data = tuple(data[i:i+2] for i in range(0, len(data), 2))  # Agrupa os dados em pares
    x = list(range(len(tuple_data)))

    # Configura posições dos elementos no eixo y
    y_positions = {"-3": 0, "-1": 2, "+1": 4, "+3": 6}
    y = [y_positions[str(value)] for value in tuple_data]

    plt.step(x, y, where='post')
    plt.yticks([0, 2, 4, 6], ['-3', '-1', '+1', '+3'])
    plt.title('Sinal codificado')
    plt.xlabel('Tempo')
    plt.ylabel('Estado')
    plt.show(block=False)

# Função para aplicar o algoritmo de codificação de linha inverso
def decode_2B1Q(data):
    # Estado inicial
    previous_level = "+1"
    # Mapeamento do algoritmo 2B1Q inverso
    previous_level_pos_inverse = {
        '+1': '00',
        '+3': '01',
        '-1': '10',
        '-3': '11'
    }
    previous_level_neg_inverse = {
        '-1': '00',
        '-3': '01',
        '+1': '10',
        '+3': '11'
    }

    bits = []

    # Estado inicial
    state = '00'

    # Percorre os bits de 2 em 2
    for i in range(0, len(data), 2):
        pair = data[i:i + 2]

        # Verifica se o par de bits está no mapeamento
        if "+" in previous_level:
            if pair in previous_level_pos_inverse:
                current_bits = previous_level_pos_inverse[pair]
            else:
                # Em caso de erro, mantém o último sinal para evitar transições abruptas
                current_bits = state

        elif "-" in previous_level:
            if pair in previous_level_neg_inverse:
                current_bits = previous_level_neg_inverse[pair]
            else:
                # Em caso de erro, mantém o último sinal para evitar transições abruptas
                current_bits = state

        else:
            # Em caso de erro, mantém o último sinal para evitar transições abruptas
            current_bits = state

        # Adiciona o sinal atual à lista de sinais
        bits.append(current_bits)
        previous_level = pair

    return ''.join(bits)

# Função para converter de binário para ASCII
def to_ascii(binary):
    ascii_data = ''
    string = ''.join(str(bit) for bit in binary)
    for i in range(0, len(string), 8):
        char = chr(int(string[i:i+8], 2))
        ascii_data += char

    return ascii_data

# Algoritmo de criptografia de modo inverso
def caeser_decrypt(data, key, mode):
    alphabet = 'abcdefghijklmnopqrstuvwyzàáãâéêóôõíúçABCDEFGHIJKLMNOPQRSTUVWYZÀÁÃÂÉÊÓÕÍÚÇ'
    new_data = ''
    for c in data:
        index = alphabet.find(c)
        if index == -1:
            new_data += c
        else:
            new_index = index + key if mode == 1 else index - key
            new_index = new_index % len(alphabet)
            new_data += alphabet[new_index:new_index+1]
    return new_data


# def print_list(lista):
#     formatted_list = ', '.join(str(item) for item in lista)  # Convert list to a formatted string with comma separator
#     text_box.insert(tk.END, formatted_list)  # Insert the formatted list into the text field

# def index_in_list(a_list, index):
#     return index < len(a_list)

# Função chamada ao receber os dados
def process_data(data):
    # Cria o gráfico
    create_graph(data)

    text_box.insert(tk.END, "Mensagem recebida: " + data + "\n\n")

    # Aplica o princípio do algoritmo de codificação de linha (2B1Q) inverso
    decoded_2b1q_data = decode_2B1Q(data)
    text_box.insert(tk.END, "Descodificação com algoritmo 2B1Q em binário: " + decoded_2b1q_data + "\n\n")

    # Binário para ASCII
    ascii_data = to_ascii(decoded_2b1q_data)
    text_box.insert(tk.END, "\n\nMensagem descriptografada em ascii: " + ascii_data + "\n\n")

    # Algortimo de criptografica (Cifra de César) inverso
    caser_decrypted_data = caeser_decrypt(ascii_data, 3, 0)
    text_box.insert(tk.END, "\n\nMensagem descriptografada: " + caser_decrypted_data + "\n\n")

    # Exibe a mensagem recebida no terminal
    print('Mensagem descriptografada:', ''.join(caser_decrypted_data))

    text_box.pack()

# Função para receber os dados pelo socket
def receive_data():
    data = client_socket.recv(1024).decode()
    return data

# Recebe os dados
root = tk.Tk()
root.title('Comunicação de Dados')
text_box = tk.Text(root)

data_received = receive_data()

# Processa os dados
process_data(data_received)

# Aguarda a entrada do usuário(matém a janela aberta)
input()

# Fecha a conexão e o socket
client_socket.close()
