#include "MainWindow.h"

#include <QFileDialog>
#include <QDir>
#include <QMessageBox>
#include <QTextStream>

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
	ui.setupUi(this);
	canvas = new Canvas(this);
	setCentralWidget(canvas);

	connect(ui.actionSave, SIGNAL(triggered()), this, SLOT(onSave()));
	connect(ui.actionOpen, SIGNAL(triggered()), this, SLOT(onOpen()));
	connect(ui.actionNext, SIGNAL(triggered()), this, SLOT(onNext()));
	connect(ui.actionPrevious, SIGNAL(triggered()), this, SLOT(onPrevious()));
	connect(ui.actionUndo, SIGNAL(triggered()), this, SLOT(onUndo()));
	connect(ui.actionExit, SIGNAL(triggered()), this, SLOT(close()));

	// load parameter file
	loadParams();
}

void MainWindow::loadImage(const QFileInfo& fileinfo) {
	canvas->loadImage(fileinfo.absoluteFilePath());
	if (all_params.contains(fileinfo.fileName())) {
		canvas->setParams(all_params[fileinfo.fileName()]);
	}
	setWindowTitle("Window Boundary Annotation - " + fileinfo.fileName());
}

void MainWindow::loadParams() {
	QFile file("facade_annotation.txt");
	if (file.exists()) {
		file.open(QIODevice::ReadOnly);
		QTextStream in(&file);
		while (!in.atEnd()) {
			QStringList list = in.readLine().split(",");

			for (int i = 1; i < list.size(); ++i) {
				all_params[list[0]].push_back(list[i].toFloat());
			}
		}
		file.close();
	}
}

void MainWindow::saveParams() {
	QFile file("facade_annotation.txt");
	file.open(QIODevice::WriteOnly);
	QTextStream out(&file);
	for (auto it = all_params.begin(); it != all_params.end(); ++it) {
		out << it.key();
		for (auto param : it.value()) {
			out << "," << param;
		}
		out << "\n";
	}
	file.close();
}

void MainWindow::onOpen() {
	QString filename = QFileDialog::getOpenFileName(this, tr("Open Image file..."), "", tr("Image Files (*.png *jpg)"));
	if (filename.isEmpty()) return;

	int index = filename.lastIndexOf("/");
	QString dirname;
	if (index >= 0) {
		dirname = filename.left(index);
		filename = filename.mid(index + 1);
	}
	else {
		dirname = ".";
	}

	// obtain file list
	QStringList filters;
	filters << "*.png" << "*.jpg" << "*.bmp";
	fileInfoList = QDir(dirname).entryInfoList(filters, QDir::Files | QDir::NoDotAndDotDot);

	for (int i = 0; i < fileInfoList.size(); ++i) {
		if (fileInfoList[i].fileName() == filename) {
			curIndex = i;
			loadImage(fileInfoList[curIndex]);
			break;
		}
	}
}

void MainWindow::onSave() {
	all_params[fileInfoList[curIndex].fileName()] = canvas->getParams();
	saveParams();
}

void MainWindow::onNext() {
	// save parameters
	all_params[fileInfoList[curIndex].fileName()] = canvas->getParams();
	saveParams();

	if (curIndex >= fileInfoList.size() - 1) {
		QMessageBox msg;
		msg.setText("No more next image.");
		msg.exec();
	}
	else {
		curIndex++;
		loadImage(fileInfoList[curIndex]);
	}
}

void MainWindow::onPrevious() {
	// save parameters
	all_params[fileInfoList[curIndex].fileName()] = canvas->getParams();
	saveParams();

	if (curIndex <= 0) {
		QMessageBox msg;
		msg.setText("No more previous image.");
		msg.exec();
	}
	else {
		curIndex--;
		loadImage(fileInfoList[curIndex]);
	}
}

void MainWindow::onUndo() {
	canvas->undo();
}