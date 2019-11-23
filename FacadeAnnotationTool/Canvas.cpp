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

	line_direction = LINE_HORIZONTAL;
}

void Canvas::paintEvent(QPaintEvent *event) {
	if (!image.isNull()) {
		QPainter painter(this);
		painter.drawImage(0, 0, image);

		painter.setPen(QPen(QColor(255, 255, 0), 3));
		for (auto pos : params) {
			if (line_direction == LINE_HORIZONTAL) {
				painter.drawLine(0, pos * image.height(), image.width(), pos * image.height());
			}
			else {
				painter.drawLine(pos * image.width(), 0, pos * image.width(), 0);
			}
		}
	}
}

void Canvas::mousePressEvent(QMouseEvent* e) {
	if (line_direction == LINE_HORIZONTAL) {
		float pos = (float)e->y() / image.height();
		params.push_back(pos);
	}
	else {
		float pos = (float)e->x() / image.width();
		params.push_back(pos);
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
	params.clear();

	update();
}

void Canvas::undo() {
	if (params.size() > 0) {
		params.pop_back();
		update();
	}
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

