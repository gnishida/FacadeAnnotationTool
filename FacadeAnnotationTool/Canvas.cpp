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

	mode = MODE_HORIZONTAL;
}

void Canvas::paintEvent(QPaintEvent *event) {
	if (!image.isNull()) {
		QPainter painter(this);
		painter.drawImage(0, 0, image);

		painter.setPen(QPen(QColor(255, 255, 0), 3));
		if (mode == MODE_HORIZONTAL) {
			for (auto pos : floorParams) {
				painter.drawLine(0, pos * image.height(), image.width(), pos * image.height());
			}
		}
		else {
			for (auto pos : columnParams) {
				painter.drawLine(pos * image.width(), 0, pos * image.width(), image.height());
			}
		}
	}
}

void Canvas::mousePressEvent(QMouseEvent* e) {
	if (mode == MODE_HORIZONTAL) {
		float pos = (float)e->y() / image.height();
		floorParams.push_back(pos);
	}
	else {
		float pos = (float)e->x() / image.width();
		columnParams.push_back(pos);
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
	floorParams.clear();
	columnParams.clear();

	update();
}

void Canvas::undo() {
	if (mode == MODE_HORIZONTAL) {
		if (floorParams.size() > 0) {
			floorParams.pop_back();
			update();
		}
	}
	else {
		if (columnParams.size() > 0) {
			columnParams.pop_back();
			update();
		}
	}
}

void Canvas::setModeHorizontal() {
	mode = MODE_HORIZONTAL;
	update();
}

void Canvas::setModeVertical() {
	mode = MODE_VERTICAL;
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

