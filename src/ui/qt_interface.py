"""
PyQt6 based Graphical User Interface for Kallisto-OSINTer.
Provides a GUI for initiating OSINT tasks, displaying results and visualizations.
"""

import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from src.agents.knowledge_agent import KnowledgeAgent
from src.config import load_config
from src.utils.logger import get_logger
from src.visualization.data_visualizer import visualize_osint_summary

logger = get_logger(__name__)

class OSINTerGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(OSINTerGUI, self).__init__()
        self.config = load_config()
        self.setWindowTitle("Kallisto-OSINTer GUI")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(layout)

        # Input field for query
        self.query_input = QtWidgets.QLineEdit()
        self.query_input.setPlaceholderText("Enter OSINT query (e.g., person lookup)...")
        layout.addWidget(self.query_input)

        # Button to run OSINT task
        self.run_button = QtWidgets.QPushButton("Run OSINT Task")
        self.run_button.clicked.connect(self.run_osint_task)
        layout.addWidget(self.run_button)

        # Text area for displaying results
        self.results_text = QtWidgets.QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        # Button for visualization
        self.visualize_button = QtWidgets.QPushButton("Visualize Results")
        self.visualize_button.clicked.connect(self.visualize_results)
        layout.addWidget(self.visualize_button)

        # Status bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)

    def run_osint_task(self):
        query = self.query_input.text().strip()
        if not query:
            self.status_bar.showMessage("Please enter a query.", 5000)
            return

        self.results_text.clear()
        self.status_bar.showMessage("Running OSINT task...")
        QtCore.QCoreApplication.processEvents()

        try:
            # For demo purposes, we use KnowledgeAgent to aggregate knowledge.
            agent = KnowledgeAgent(query, self.config, rounds=1)
            knowledge = agent.aggregate_knowledge()
            final_answer = agent.answer_final_question("Summarize the OSINT findings.")
            self.results_text.append("Aggregated Knowledge:\n" + knowledge)
            self.results_text.append("\nFinal Answer:\n" + final_answer)
            self.status_bar.showMessage("OSINT task completed.", 5000)
            # Store aggregated knowledge for visualization
            self.osint_summary = knowledge
        except Exception as e:
            self.results_text.append("Error during OSINT task: " + str(e))
            self.status_bar.showMessage("Error occurred.", 5000)

    def visualize_results(self):
        if hasattr(self, 'osint_summary'):
            self.status_bar.showMessage("Generating visualizations...")
            vis_paths = visualize_osint_summary(self.osint_summary)
            message = "Visualizations generated:\n"
            for key, path in vis_paths.items():
                message += f"{key}: {path}\n"
            self.results_text.append("\n" + message)
            self.status_bar.showMessage("Visualizations generated.", 5000)
        else:
            self.status_bar.showMessage("No OSINT summary available for visualization.", 5000)

def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = OSINTerGUI()
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()