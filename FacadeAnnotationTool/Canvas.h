#ifndef CANVAS_H
#define CANVAS_H

#include <QWidget>
#include <QKeyEvent>

class Canvas : public QWidget {
private:
	static enum { LINE_HORIZONTAL = 0, LINE_VERTICAL };

private:
	QImage orig_image;
	QImage image;
	std::vector<float> params;
	std::vector<float> predicted_params;
	int line_direction;

	bool ctrlPressed;
	bool shiftPressed;
	
public:
	Canvas(QWidget *parent = NULL);
	
protected:
	void paintEvent(QPaintEvent *event);
	void mousePressEvent(QMouseEvent* e);
	void resizeEvent(QResizeEvent *e);

public:
	void setParams(const std::vector<float>& params) { this->params = params; }
	void setPredictedParams(const std::vector<float>& params) { this->predicted_params = params; }
	std::vector<float> getParams() { return params; }
	void loadImage(const QString& filename);
	void undo();
	void keyPressEvent(QKeyEvent* e);
	void keyReleaseEvent(QKeyEvent* e);
};

#endif // CANVAS_H
