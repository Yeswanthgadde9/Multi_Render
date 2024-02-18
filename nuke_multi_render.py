import sys
import os
import subprocess
import psutil
import glob
import nuke
import nukescripts
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
path = os.path.dirname(__file__)
sys.path.insert(0, "{}/{}".format(path, "Ui"))
from render_submitter_ui import Ui_Form


NODE_CLASS = ("Write", "DeepWrite")


class RenderOrder:
    def __init__(self):
        self.dep_write_nodes = dict()
        self.write_data = dict()
        self.set_render_order()

    def find_dep(self, node):
        """
        Function to find dependent write nodes
        :param node: write or deep write
        :return: None
        """
        write_nodes = []
        prim_dep = node.dependencies()
        while prim_dep:
            dep_node = prim_dep.pop()
            if dep_node:
                prim_dep.extend(dep_node.dependencies())
                if dep_node not in write_nodes and dep_node.Class() in NODE_CLASS:
                    write_nodes.append(dep_node)
                    self.dep_write_nodes[node] = write_nodes

    def set_render_order(self):
        """
        Function to set render order for all write and deep write nodes
        :return: None
        """
        all_write_nodes = nuke.allNodes("Write") + nuke.allNodes("DeepWrite")
        for write in all_write_nodes:
            write["render_order"].setValue(1)
            self.find_dep(write)
        sorted_dict = dict(sorted(self.dep_write_nodes.items(), key=lambda x: len(x[1])))
        for key, value in sorted_dict.items():
            if len(value) == 1:
                key["render_order"].setValue(key["render_order"].value() + 1)
            else:
                max_ro = max(map(lambda x: x["render_order"].value(), value))
                key["render_order"].setValue(max_ro + 1)


class RenderWidget(QWidget, Ui_Form):
    def __init__(self):
        """
        Main class to initialize render widget UI
        """
        super(RenderWidget, self).__init__()
        self.nodes = None
        self.nodes_to_render = dict()
        self.write_dependencies = dict()
        self.create_reads = dict()
        self.render_id = dict()
        self.render_threads = dict()
        self.finished_count = 0
        self.render_count = 0
        RenderOrder()
        self.get_write_nodes()
        self.setupUi(self)
        self.update_widget()
        self.pushButton.clicked.connect(self.cancel)
        self.pushButton_2.clicked.connect(self.submit_render)
        self.pushButton_3.clicked.connect(self.update_ui)
        self.pushButton_4.clicked.connect(self.load_read_nodes)

    def update_ui(self):
        """
        Function to update Ui
        :return: None
        """
        self.nodes_to_render.clear()
        self.get_write_nodes()
        RenderOrder()
        self.update_widget()

    def get_write_nodes(self):
        """
        Function to get write nodes from the scene
        :return: None
        """
        nodes = nuke.selectedNodes()
        if nodes:
            self.nodes = [node for node in nodes if node.Class() in NODE_CLASS]

        else:
            self.nodes = nuke.allNodes("Write") + nuke.allNodes("DeepWrite")

    def update_widget(self):
        """
        Function to update render widget Ui
        :return: None
        """
        self.tableWidget.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.sorted_write_nodes = sorted(self.nodes, key=lambda node: node['render_order'].value())
        self.find_dep_nodes()
        self.tableWidget.setRowCount(len(self.sorted_write_nodes))
        for index, item in enumerate(self.sorted_write_nodes):
            self.node_name = QTableWidgetItem(item.name())
            self.node_name.setFlags(self.node_name.flags() ^ Qt.ItemIsEditable)
            self.tableWidget.setItem(index, 0, self.node_name)
            self.frame_range = "{}-{}".format(item.firstFrame(), item.lastFrame())
            self.tableWidget.setItem(index, 1, QTableWidgetItem(self.frame_range))
            self.render_order_value = str(int(item["render_order"].value()))
            self.render_order = QTableWidgetItem(self.render_order_value)
            self.render_order.setFlags(self.render_order.flags() ^ Qt.ItemIsEditable)
            self.tableWidget.setItem(index, 3, self.render_order)
            self.status_label = QLabel()
            self.status_label.setText("Waiting")
            self.status_label.setAlignment(Qt.AlignCenter)
            self.tableWidget.setCellWidget(index, 4, self.status_label)
            self.tableWidget.setItem(index, 5, QTableWidgetItem(item.name()))
            self.channels_combo_box = QComboBox()
            self.channels_combo_box.addItems([item["channels"].value(), 'all', 'none', 'rgb', 'rgba', 'alpha'])
            self.tableWidget.setCellWidget(index, 2, self.channels_combo_box)
            self.after_render_combo_box = QComboBox()
            self.after_render_combo_box.addItems(['None', 'Create Read Node'])
            self.tableWidget.setCellWidget(index, 5, self.after_render_combo_box)
            self.render_progress_bar = QProgressBar()
            self.render_progress_bar.setMinimumWidth(100)
            self.tableWidget.setCellWidget(index, 6, self.render_progress_bar)
            self.cancel_button = QPushButton()
            self.cancel_button.setEnabled(False)
            self.cancel_button.setText("Cancel")
            self.cancel_button.clicked.connect(self.on_button_clicked)
            self.tableWidget.setCellWidget(index, 7, self.cancel_button)

    def render_data(self):
        """
        Function to get render data from write nodes
        :return: None
        """
        for index, node in enumerate(self.sorted_write_nodes):
            write_node = self.tableWidget.item(index, 0).text()
            frame_range = self.tableWidget.item(index, 1).text()
            channels_combo_box = self.tableWidget.cellWidget(index, 2)
            channels = channels_combo_box.currentText()
            node["channels"].setValue(channels)
            after_render = self.tableWidget.cellWidget(index, 5).currentText()
            if after_render != "None":
                self.create_reads[nuke.toNode(write_node)] = frame_range
            render_order = node["render_order"].value()
            if render_order not in self.nodes_to_render:
                self.nodes_to_render[render_order] = []
            self.nodes_to_render[render_order].append(
                {"name": write_node, "frame_range": frame_range, "channels": channels, "position": index})

    def submit_render(self):
        """
        Function to submit render
        :return:
        """
        self.render_data()
        self.launch_render()

    def find_dep_nodes(self):
        """
        Find write/deep write dependencies
        :return:
        """
        node_in_use = self.sorted_write_nodes.copy()
        while node_in_use:
            node = node_in_use.pop(0)
            if node not in self.write_dependencies.keys():
                self.write_dependencies[node.name()] = []
            self.write_dependencies[node.name()].extend(node.dependencies())
            if len(self.write_dependencies[node.name()]) != 0:
                for dep in self.write_dependencies[node.name()]:
                    sc_dep = dep.dependencies()
                    if sc_dep and sc_dep not in self.write_dependencies[node.name()]:
                        self.write_dependencies[node.name()].extend(sc_dep)

    def launch_render(self):
        """
        Function to gather render information and start render threads
        :return: None
        """
        for k, v in self.nodes_to_render.items():
            for node in v:
                self.render_count = len(self.nodes_to_render[k])
                name = node["name"]
                frames = node["frame_range"]
                row = node["position"]
                nukescripts.clear_selection_recursive()
                write_node = nuke.toNode(name)
                write_node["disable"].setValue(False)
                for s in self.write_dependencies[name]:
                    s.setSelected(True)
                write_node.setSelected(True)
                file_path = "/".join(write_node["file"].value().split("/")[0:-1])
                if not os.path.exists(file_path):
                    os.mkdir(file_path)
                nuke_file = write_node["file"].value().split(".")[0] + ".nk"
                nuke.nodeCopy(nuke_file)
                nukescripts.clear_selection_recursive()
                render_task = RenderTask(self, name, frames, row)
                render_task.start()
                cancel_button = self.tableWidget.cellWidget(row, 7)
                cancel_button.setEnabled(True)
                self.update_label(row, "Running")
                render_task.signals.label_update.connect(self.update_label)
                render_task.signals.progress_updated.connect(self.update_progress)
                render_task.signals.finished.connect(self.call_render)
                self.render_threads[name] = render_task
            del self.nodes_to_render[k]
            break

    def call_render(self):
        """
        Signal to initialize renders
        :return:
        """
        self.finished_count += 1
        if self.finished_count == self.render_count:
            self.finished_count = 0
            self.launch_render()

    def load_read_nodes(self):
        """
        Function to load read nodes and connect them in the tree
        :return:
        """
        self.create_reads.clear()
        self.render_data()
        for node, frame in self.create_reads.items():
            node["disable"].setValue(True)
            dependent_nodes = node.dependent()
            dependent_nodes = [node for node in dependent_nodes if node.Class() != "Viewer"]
            if node.Class() == "Write":
                read = nuke.nodes.Read()
                custom_tab = nuke.Tab_Knob('custom', 'Custom')
                read.addKnob(custom_tab)
                read.addKnob(nuke.PyScript_Knob('load_nuke_script', 'Load Nuke Script',
                                                'nuke_multi_render.RenderWidget.load_script()'))
                read_path = "{} {}-{}".format(node['file'].value(), frame.split("-")[0], frame.split("-")[1])
                read["file"].fromUserText(read_path)
                read.setXYpos(node.xpos() + 150, node.ypos() + 10)
                switch = nuke.nodes.Switch()
                switch.setInput(0, read)
                switch.setInput(1, node)
                switch.setXYpos(node.xpos(), node.ypos() + 50)
                for d in dependent_nodes:
                    inputs = d.inputs()
                    if inputs == 1:
                        d.setInput(0, switch)
                    else:
                        for i in range(inputs):
                            if d.input(i).name() == node.name():
                                d.setInput(i, switch)
            elif node.Class() == "DeepWrite":
                deep_read = nuke.createNode("DeepRead")
                deep_read_path = "{} {}-{}".format(node['file'].value(), 1, 5)
                deep_read["file"].fromUserText(deep_read_path)
                deep_read.setXYpos(node.xpos() + 0, node.ypos() + 50)
                for dep in dependent_nodes:
                    inputs = dep.inputs()
                    if inputs == 1:
                        dep.setInput(0, deep_read)
                    else:
                        for i in range(inputs):
                            if dep.input(i).name() == node.name():
                                dep.setInput(i, deep_read)

    @staticmethod
    def load_script():
        """
        Function to import render script and hook it back
        :return: None
        """
        node = nuke.thisNode()
        dependent_nodes = node.dependent()
        dependent_nodes = [node for node in dependent_nodes if node.Class() != "Viewer"]
        file_path = node['file'].value()
        directory = "/".join(file_path.split("/")[:-1])
        nk_files = glob.glob(os.path.join(directory, "*.nk"))
        nuke_file = nk_files[0].replace("\\", "/")
        base_name = os.path.basename(nuke_file)
        nukescripts.clear_selection_recursive()
        last_node = nuke.nodePaste(nuke_file)
        bd = nukescripts.autoBackdrop()
        bd["label"].setValue("<center>"+base_name)
        bd["note_font"].setValue("Bold")
        bd["note_font_size"].setValue(30)
        nukescripts.clear_selection_recursive()
        node.setXYpos(node.xpos() + 50, node.ypos() + 10)
        switch = nuke.nodes.Switch()
        switch.setInput(0, node)
        switch.setInput(1, last_node)
        switch.setXYpos(node.xpos(), node.ypos())
        switch["which"].setValue(1)
        for d in dependent_nodes:
            inputs = d.inputs()
            if inputs == 1:
                d.setInput(0, switch)
            else:
                for i in range(inputs):
                    if d.input(i).name() == node.name():
                        d.setInput(i, switch)

    def update_progress(self, value, row):
        """
        Function to update progressbar
        :param value: value to update progressbar(type:int)
        :param row: row number of the progress bar(type:int)
        :return: None
        """
        p_bar = self.tableWidget.cellWidget(row, 6)
        if isinstance(p_bar, QProgressBar):
            p_bar.setValue(value)

    def update_label(self, row, text):
        """
        Function to update render status
        :param row: row number of the label(type:int)
        :param text: text to update the label(type:str)
        :return: None
        """
        label = self.tableWidget.cellWidget(row, 4)
        if isinstance(label, QLabel):
            label.setText(text)
            if text == "Running":
                label.setStyleSheet("color: rgb(242, 156, 54)")
            elif text == "Cancelled" or text == "Failed":
                label.setStyleSheet("color: rgb(242, 0, 0)")
            else:
                label.setStyleSheet("color: rgb(85, 255, 0)")

    def on_button_clicked(self):
        """
        Cancel button slot
        :return: None
        """
        button = self.sender()
        if not button:
            return
        index = self.tableWidget.indexAt(button.pos())
        row = index.row()
        write = self.tableWidget.item(row, 0).text()
        pid = self.render_id[write]
        thread = self.render_threads[write]
        if pid and psutil.pid_exists(pid):
            try:
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
                thread.terminate()
                self.update_label(row, "Cancelled")
                p_bar = self.tableWidget.cellWidget(row, 6)
                p_bar.setStyleSheet("QProgressBar::chunk {background:red}")
                self.call_render()
            except Exception as e:
                print("Error terminating process {}: {}".format(pid, e))
                raise

    def cancel(self):
        """
        Cancel button function to kill renders and close ui
        :return:
        """
        if self.render_id and self.render_threads:
            for val in self.render_id.values():
                if psutil.pid_exists(val):
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', str(val)], check=True)
                    except Exception as e:
                        print("Error {}".format(e))
                        raise
        self.close()


class RenderTaskSignals(QObject):
    """
    Qthread signals
    """
    progress_updated = Signal(int, int)
    label_update = Signal(int, str)
    finished = Signal()


class RenderTask(QThread):
    def __init__(self, render_widget, write_node, total_frames, row):
        """
        Thread subclass to initialize render
        :param render_widget: RenderWidget class
        :param write_node: Name of the write node(type:str)
        :param total_frames: Frame range (type:str)
        :param row: row number of the write node (type:int)
        """
        super(RenderTask, self).__init__()
        self.render_widget = render_widget
        self.comp_node = write_node
        self.total_frames = total_frames
        self.row = row
        self.nuke_script = nuke.root()["name"].value()
        self.signals = RenderTaskSignals()

    def run(self):
        try:
            nuke_exec_path = sys.executable
            nuke_render_cmd = r'"{}" -X "{}" "{}" "{}"'.format(
                nuke_exec_path,
                self.comp_node,
                self.nuke_script,
                self.total_frames
            )
            render_process = subprocess.Popen(nuke_render_cmd, stdout=subprocess.PIPE, shell=True)
            pid = render_process.pid
            if self.comp_node not in self.render_widget.render_id.keys():
                self.render_widget.render_id[self.comp_node] = pid
            for line in render_process.stdout:
                render_log = line.strip().decode('utf-8')
                if render_log.startswith("Frame"):
                    value = render_log.split(" ")[1]
                    progress_value = int(value) / int(self.total_frames.split("-")[-1]) * 100
                    self.signals.progress_updated.emit(progress_value, self.row)
                    if progress_value == 100:
                        self.signals.label_update.emit(self.row, "Completed")
                        self.signals.finished.emit()
        except Exception as e:
            print("Error rendering {}: {}".format(self.comp_node, e))


def main():
    main.widgets = RenderWidget()
    main.widgets.show()
