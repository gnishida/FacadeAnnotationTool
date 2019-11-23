#ifndef CANVAS_H
#define CANVAS_H

#include <QWidget>
#include <QKeyEvent>

class Canvas : public QWidget {
private:
	static enum { TOP_LEFT = 0, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT };

private:
	QImage orig_image;
	QImage image;
	std::vector<float> params;
	int click_cnt;

	bool ctrlPressed;
	bool shiftPressed;
	
public:
	Canvas(QWidget *parent = NULL);

	void setParams(const std::vector<float>& params) { this->params = params; }
	std::vector<float> getParams() { return params;  }
	
protected:
	void paintEvent(QPaintEvent *event);
	void mousePressEvent(QMouseEvent* e);
	void resizeEvent(QResizeEvent *e);

public:
	void loadImage(const QString& filename);
	void keyPressEvent(QKeyEvent* e);
	void keyReleaseEvent(QKeyEvent* e);
};

#endif // CANVAS_H
