#include "Canvas.h"
#include <QPainter>
#include <iostream>
#include <QFileInfoList>
#include <QDir>
#include <QMessageBox>
#include <QTextStream>
#include <QResizeEvent>


Canvas::Canvas(QWidget *parent) : QWidget(parent) {
	ctrlPressed = false;
	shiftPressed = false;

	params.resize(4);
	params[0] = 0.2;
	params[1] = 0.2;
	params[2] = 0.8;
	params[3] = 0.8;
}

void Canvas::paintEvent(QPaintEvent *event) {
	if (!image.isNull()) {
		QPainter painter(this);
		painter.drawImage(0, 0, image);

		painter.setPen(QPen(QColor(255, 255, 0), 3));
		painter.drawRect(params[0] * image.width(), params[1] * image.height(), (params[2] - params[0]) * image.width(), (params[3] - params[1]) * image.height());
	}
}

void Canvas::mousePressEvent(QMouseEvent* e) {
	if (click_cnt == 0) {
		params[0] = (float)e->x() / image.width();
		params[1] = (float)e->y() / image.height();
		click_cnt++;
	}
	else {
		params[2] = (float)e->x() / image.width();
		params[3] = (float)e->y() / image.height();
		click_cnt = 0;
	}

	update();
}

void Canvas::resizeEvent(QResizeEvent *e) {
	if (!orig_image.isNull()) {
		float scale = std::min((float)width() / orig_image.width(), (float)height() / orig_image.height());
		image = orig_image.scaled(orig_image.width() * scale, orig_image.height() * scale);
	}
}

void Canvas::loadImage(const QString& filename) {
	orig_image = QImage(filename);
	float scale = std::min((float)width() / orig_image.width(), (float)height() / orig_image.height());
	image = orig_image.scaled(orig_image.width() * scale, orig_image.height() * scale);
	click_cnt = 0;

	update();
}

void Canvas::keyPressEvent(QKeyEvent* e) {
	ctrlPressed = false;
	shiftPressed = false;

	if (e->modifiers() & Qt::ControlModifier) {
		ctrlPressed = true;
	}
	if (e->modifiers() & Qt::ShiftModifier) {
		shiftPressed = true;
	}

	switch (e->key()) {
	case Qt::Key_Space:
		break;
	}

	update();
}

void Canvas::keyReleaseEvent(QKeyEvent* e) {
	switch (e->key()) {
	case Qt::Key_Control:
		ctrlPressed = false;
		break;
	case Qt::Key_Shift:
		shiftPressed = false;
		break;
	default:
		break;
	}
}

