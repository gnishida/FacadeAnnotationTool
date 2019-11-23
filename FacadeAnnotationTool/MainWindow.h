#pragma once

#include <QtWidgets/QMainWindow>
#include "ui_MainWindow.h"
#include "Canvas.h"
#include <QFileInfoList>

class MainWindow : public QMainWindow
{
    Q_OBJECT

private:
	Ui::MainWindowClass ui;
	Canvas* canvas;
	QFileInfoList fileInfoList;
	int curIndex;

public:
    MainWindow(QWidget *parent = Q_NULLPTR); 

	void loadImage(const QString& filename);

public slots:
	void onOpen();
	void onSave();
	void onNext();
	void onPrevious();
};
