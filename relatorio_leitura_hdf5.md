# Relatório: Como funciona a leitura de um arquivo HDF5

## O que é um arquivo HDF5?
O HDF5 (Hierarchical Data Format version 5) é um formato de arquivo binário projetado para armazenar e organizar grandes volumes de dados numéricos e científicos. Ele permite a criação de uma estrutura hierárquica (semelhante a pastas e arquivos) dentro de um único arquivo, facilitando o armazenamento de múltiplos datasets, metadados e atributos.

## Estrutura de um arquivo HDF5
- **Grupos (Groups):** Funcionam como pastas, podendo conter outros grupos ou datasets.
- **Datasets:** São arrays multidimensionais de dados (ex: matrizes, séries temporais, imagens).
- **Atributos:** Metadados associados a grupos ou datasets (ex: descrição, unidades, data de aquisição).

Exemplo de estrutura:
```
/
├── sensors/
│   ├── multi_sensor (dataset)
│   └── vibration_3axis (dataset)
├── signals/
│   └── sine_wave (dataset)
├── environmental/
│   ├── temperature (dataset)
│   └── pressure (dataset)
└── time_axis (dataset)
```

## Como funciona a leitura de um arquivo HDF5 em Python
A leitura é feita geralmente com a biblioteca `h5py`, que permite navegar pela estrutura hierárquica e acessar dados e atributos.

### Passos básicos:
1. **Abrir o arquivo:**
```python
import h5py
f = h5py.File('arquivo.h5', 'r')
```

2. **Navegar pela estrutura:**
```python
# Listar grupos e datasets na raiz
def print_structure(g, prefix=""):
    for key in g:
        item = g[key]
        path = f"{prefix}/{key}" if prefix else key
        if isinstance(item, h5py.Group):
            print(f"Grupo: {path}/")
            print_structure(item, path)
        else:
            print(f"Dataset: {path}  shape={item.shape} dtype={item.dtype}")

print_structure(f)
```

3. **Ler dados de um dataset:**
```python
data = f['sensors/multi_sensor'][:]
print(data.shape)
```

4. **Ler atributos:**
```python
attrs = f['sensors/multi_sensor'].attrs
for key in attrs:
    print(f"{key}: {attrs[key]}")
```

5. **Fechar o arquivo:**
```python
f.close()
```

## Dicas importantes
- Sempre abra arquivos HDF5 no modo leitura ('r') se não for modificar.
- Use a navegação hierárquica para explorar a estrutura.
- Datasets podem ser grandes: evite carregar tudo na memória se não for necessário (use slicing).
- Atributos são úteis para entender o contexto dos dados.

## Exemplo prático
```python
import h5py

with h5py.File('sample_multichannel_data.h5', 'r') as f:
    # Listar todos os datasets
    def list_datasets(g, prefix=""):
        for key in g:
            item = g[key]
            path = f"{prefix}/{key}" if prefix else key
            if isinstance(item, h5py.Group):
                list_datasets(item, path)
            else:
                print(f"{path}: shape={item.shape} dtype={item.dtype}")
    list_datasets(f)
    
    # Ler um dataset específico
    data = f['sensors/multi_sensor'][:100, :]
    print(data)
    
    # Ler atributos
    attrs = f['sensors/multi_sensor'].attrs
    print(dict(attrs))
```

## Conclusão
A leitura de arquivos HDF5 é eficiente e flexível, permitindo acessar grandes volumes de dados organizados de forma hierárquica, além de metadados essenciais para análise científica e industrial.
