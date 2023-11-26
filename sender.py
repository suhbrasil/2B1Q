import tkinter as tk
import socket
import matplotlib.pyplot as plt



# Configurações de rede
HOST = '192.168.1.6'  # Endereço IP do computador servidor
PORT = 12346       # Porta para a conexão

# Cria um objeto de socket (socket permite a troca de dados entre processos, máquinas ou dispositivos por meio de uma rede)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Associa o socket ao endereço IP e à porta
server_socket.bind((HOST, PORT))

# Coloca o socket em modo de escuta
server_socket.listen(1)

print('Aguardando conexão...')

# Aceita a conexão do cliente
client_socket, addr = server_socket.accept()

print('Conexão estabelecida de:', addr)

# Cifra de Cesar
# Funciona a partir da substituição das letras do alfabeto por outras, n vezes, conforme a chave de criptografia utilizada.
# Para encriptografar, troca toda a letra do alfabeto por outra n (key) vezes na sua frente.
# Para descriptografar, troca toda a letra do alfabeto por outra n (key) vezes para trás.
# https://medium.com/vacatronics/cifra-de-c%C3%A9sar-em-python-8d02d3bc7d42 - alfabeto retirado dessa fonte
# Para tudo bem com a chave 3: tudo bem -> wxgr ehp
def caesar_encrypt(data, key, mode):
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


# Transforma a mensagem original em ascii
def ascii_encode(string):
    ascii = []
    for char in string:
        # a função ord obtem o valor ascii correspondente ao caracter
        ascii.append(ord(char))

    formatted_list = ', '.join(str(item) for item in ascii)  # Converte uma lista para uma string com virgula como separador
    text_box.insert(tk.END, formatted_list)  # Coloca a lista formatada no campo de texto
    return ascii

# Converte ascii para binário
def to_binary(ascii):
    binary = ""
    for valor in ascii:
        # a função bin retorna o binário do valor com Ob na frente, então pega da posição dois em diante
        # zfill(8) para garantir que a representação binária tem 8 bits (se não tiver ele coloca zeros à esquerda)
        binary += bin(valor)[2:].zfill(8)
    return binary

# Função para aplicar o algoritmo 2B1Q
def apply_2B1Q(data):
    # Estado inicial
    previous_level = "+1"
    # Mapeamento do algoritmo 2B1Q para cada par de bits
    previous_level_pos = {
        '00': '+1',
        '01': '+3',
        '10': '-1',
        '11': '-3'
    }
    previous_level_neg = {
        '00': '-1',
        '01': '-3',
        '10': '+1',
        '11': '+3'
    }

    signal = []

    # Percorre os bits de 2 em 2
    for i in range(0, len(data), 2):
        pair = data[i:i + 2]

        # Verifica se o par de bits está no mapeamento
        if "+" in previous_level:
            if pair in previous_level_pos:
                current_signal = previous_level_pos[pair]
            else:
                # Em caso de erro, mantém o último sinal para evitar transições abruptas
                current_signal = previous_level

        elif "-" in previous_level:
            if pair in previous_level_neg:
                current_signal = previous_level_neg[pair]
            else:
                # Em caso de erro, mantém o último sinal para evitar transições abruptas
                current_signal = previous_level

        else:
            # Em caso de erro, mantém o último sinal para evitar transições abruptas
            current_signal = previous_level

        # Adiciona o sinal atual à lista de sinais
        signal.append(current_signal)
        previous_level = current_signal

    return ''.join(signal)


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


# Função para enviar os dados pelo socket
def send_data(data):
    encoded = data.encode()
    client_socket.sendall(encoded)


# Função chamada ao clicar no botão
def send_text():
    text = entry.get()  # Obtém o texto digitado
    text_box.insert(tk.END, "Mensagem original:" + text + "\n\n")

    # algoritmo de criptografia
    caesar_text = caesar_encrypt(text, 3, 1)
    text_box.insert(tk.END, "Mensagem criptografada:" + caesar_text + "\n\n")

    # Transforma em ascii estendido
    text_box.insert(tk.END, "Mensagem criptografa em ascii:")
    ascii_text = ascii_encode(caesar_text)

    # Converte para binário
    binary_data = to_binary(ascii_text)
    text_box.insert(tk.END, "\n\nAscii em binário:" + binary_data + "\n\n")

    # Aplica a criptografia 2B1Q
    data_2b1q = apply_2B1Q(binary_data)
    text_box.insert(tk.END, "Binário codificado com 2B1Q:" + data_2b1q + "\n\n")

    text_box.pack()

    # Cria e exibe o gráfico
    create_graph(data_2b1q)

    # Envia os dados para o outro computador
    send_data(data_2b1q)

# Configuração da interface gráfica usando tkinter
root = tk.Tk()
root.title('Comunicação de Dados')

label = tk.Label(root, text='Digite o texto:')
label.pack()

entry = tk.Entry(root, width=50)
entry.pack()

button = tk.Button(root, text='Enviar', command=send_text)
button.pack()

text_box = tk.Text(root)

root.mainloop()

# Fecha o socket
server_socket.close()
