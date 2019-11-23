#include "MainWindow.h"

#include <QFileDialog>
#include <QDir>
#include <QMessageBox>

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
	ui.setupUi(this);
	canvas = new Canvas(this);
	setCentralWidget(canvas);

	connect(ui.actionSave, SIGNAL(triggered()), this, SLOT(onSave()));
	connect(ui.actionOpen, SIGNAL(triggered()), this, SLOT(onOpen()));
	connect(ui.actionNext, SIGNAL(triggered()), this, SLOT(onNext()));
	connect(ui.actionPrevious, SIGNAL(triggered()), this, SLOT(onPrevious()));
	connect(ui.actionExit, SIGNAL(triggered()), this, SLOT(close()));
}

void MainWindow::loadImage(const QString& filename) {
	canvas->loadImage(filename);
	/*
	if (all_params.contains(filename)) {
		canvas->setParams(all_params[filename]);
	}
	*/
	setWindowTitle("Window Boundary Annotation - " + filename);
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
			loadImage(fileInfoList[curIndex].absoluteFilePath());
			break;
		}
	}
}

void MainWindow::onSave() {
	//all_params[fileInfoList[curIndex].fileName()] = canvas->getParams();
	//saveParams();
}

void MainWindow::onNext() {
	// save parameters
	//all_params[fileInfoList[curIndex].fileName()] = canvas->getParams();
	//saveParams();

	if (curIndex >= fileInfoList.size() - 1) {
		QMessageBox msg;
		msg.setText("No more next image.");
		msg.exec();
	}
	else {
		curIndex++;
		loadImage(fileInfoList[curIndex].absoluteFilePath());
	}
}

void MainWindow::onPrevious() {
	// save parameters
	//all_params[fileInfoList[curIndex].fileName()] = canvas->getParams();
	//saveParams();

	if (curIndex <= 0) {
		QMessageBox msg;
		msg.setText("No more previous image.");
		msg.exec();
	}
	else {
		curIndex--;
		loadImage(fileInfoList[curIndex].absoluteFilePath());
	}
}
