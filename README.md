
# AutoGecko Project

![Auto Gecko Mascot](auto_gecko.png)

Welcome to the **AutoGecko Project**! This project is designed test an ai capability in generating and executing Python code snippets . The project features a mascot, **Auto Gecko**, who represents the automation and simplicity behind the scenes. This project is supposed to be the simplest example of an automated agent that can run code.

## Project Overview

AutoGecko is a Python-based tool that integrates with Ollama's `llama3.1` model and utilizes FAISS for efficient vector storage. The goal of AutoGecko is to make it easier to generate and run Python code by simply querying the agent with a question or a task description.

## Features

- **AI-Powered Code Generation**: Generate Python code snippets on the fly using the Ollama `llama3.1` model.
- **FAISS Vector Store**: Efficiently store and retrieve context and code snippets using FAISS.
- **Error Handling**: Automatically capture and log errors encountered during code execution.
- **Short-Term Memory**: Keep track of the last few queries and responses to maintain context.
- **Caching**: Save executed code in a cache folder for easy reference and reuse.
- **KISS**: KEEP IT SIMPLE STUPID. the code should be simple and the results, stupid. this is just a demo of how an automated agent can run code. it is fun interacting with it though.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Install the required Python packages:
  ```bash
  pip install faiss-cpu langchain huggingface-hub
  ```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AutoGeckoProject.git
   cd AutoGeckoProject
   ```

2. Run the project:
   ```bash
   python auto.py
   ```

3. Interact with the AutoGecko by entering queries in the terminal.

### Usage

Simply run the script and start typing your queries. AutoGecko will generate Python code based on your input and execute it. The code, along with any errors encountered, will be saved in the `cache` folder.

### Example Query

```plaintext
Enter your request: Create a function to calculate the factorial of a number.
```

### Auto Gecko Mascot

![Auto Gecko Mascot](/auto_gecko.png)

**Auto Gecko** is your friendly guide through this project. The mascot embodies the agility and intelligence of automation, helping you navigate through code generation and execution with ease.

## Contributing

We welcome contributions! If you have any ideas, suggestions, or bug reports, feel free to open an issue or submit a pull request.

### How to Contribute

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-branch-name
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add some feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-branch-name
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or suggestions, please contact us at `ulissescasemiro@gmail.com`.

---

Thank you for checking out the AutoGecko Project! We hope you find it as helpful and fun as we do. Happy coding!
