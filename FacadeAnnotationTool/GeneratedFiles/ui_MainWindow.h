/********************************************************************************
** Form generated from reading UI file 'MainWindow.ui'
**
** Created by: Qt User Interface Compiler version 5.6.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindowClass
{
public:
    QAction *actionExit;
    QAction *actionOpen;
    QAction *actionSave;
    QAction *actionPrevious;
    QAction *actionNext;
    QWidget *centralWidget;
    QMenuBar *menuBar;
    QMenu *menuFile;
    QToolBar *mainToolBar;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *MainWindowClass)
    {
        if (MainWindowClass->objectName().isEmpty())
            MainWindowClass->setObjectName(QStringLiteral("MainWindowClass"));
        MainWindowClass->resize(600, 400);
        actionExit = new QAction(MainWindowClass);
        actionExit->setObjectName(QStringLiteral("actionExit"));
        actionOpen = new QAction(MainWindowClass);
        actionOpen->setObjectName(QStringLiteral("actionOpen"));
        actionSave = new QAction(MainWindowClass);
        actionSave->setObjectName(QStringLiteral("actionSave"));
        actionPrevious = new QAction(MainWindowClass);
        actionPrevious->setObjectName(QStringLiteral("actionPrevious"));
        actionNext = new QAction(MainWindowClass);
        actionNext->setObjectName(QStringLiteral("actionNext"));
        centralWidget = new QWidget(MainWindowClass);
        centralWidget->setObjectName(QStringLiteral("centralWidget"));
        MainWindowClass->setCentralWidget(centralWidget);
        menuBar = new QMenuBar(MainWindowClass);
        menuBar->setObjectName(QStringLiteral("menuBar"));
        menuBar->setGeometry(QRect(0, 0, 600, 21));
        menuFile = new QMenu(menuBar);
        menuFile->setObjectName(QStringLiteral("menuFile"));
        MainWindowClass->setMenuBar(menuBar);
        mainToolBar = new QToolBar(MainWindowClass);
        mainToolBar->setObjectName(QStringLiteral("mainToolBar"));
        MainWindowClass->addToolBar(Qt::TopToolBarArea, mainToolBar);
        statusBar = new QStatusBar(MainWindowClass);
        statusBar->setObjectName(QStringLiteral("statusBar"));
        MainWindowClass->setStatusBar(statusBar);

        menuBar->addAction(menuFile->menuAction());
        menuFile->addAction(actionOpen);
        menuFile->addAction(actionSave);
        menuFile->addSeparator();
        menuFile->addAction(actionPrevious);
        menuFile->addAction(actionNext);
        menuFile->addSeparator();
        menuFile->addAction(actionExit);

        retranslateUi(MainWindowClass);

        QMetaObject::connectSlotsByName(MainWindowClass);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindowClass)
    {
        MainWindowClass->setWindowTitle(QApplication::translate("MainWindowClass", "MainWindow", Q_NULLPTR));
        actionExit->setText(QApplication::translate("MainWindowClass", "Exit", Q_NULLPTR));
        actionOpen->setText(QApplication::translate("MainWindowClass", "Open", Q_NULLPTR));
        actionOpen->setShortcut(QApplication::translate("MainWindowClass", "Ctrl+O", Q_NULLPTR));
        actionSave->setText(QApplication::translate("MainWindowClass", "Save", Q_NULLPTR));
        actionSave->setShortcut(QApplication::translate("MainWindowClass", "Ctrl+S", Q_NULLPTR));
        actionPrevious->setText(QApplication::translate("MainWindowClass", "Previous", Q_NULLPTR));
        actionPrevious->setShortcut(QApplication::translate("MainWindowClass", "Left", Q_NULLPTR));
        actionNext->setText(QApplication::translate("MainWindowClass", "Next", Q_NULLPTR));
        actionNext->setShortcut(QApplication::translate("MainWindowClass", "Right", Q_NULLPTR));
        menuFile->setTitle(QApplication::translate("MainWindowClass", "File", Q_NULLPTR));
    } // retranslateUi

};

namespace Ui {
    class MainWindowClass: public Ui_MainWindowClass {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
