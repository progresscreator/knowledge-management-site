Egghead myself;
// Some constants
float icon_size = 50;
float icon_radius = 24;

float icon_side = 50;

float font_size = 13;
PFont font=loadFont(font_url);
ArrayList eggheads;
int max_link = 0;
int num_egghead = 0;
float center_x, center_y;
// color from = color(#348781);
// color to = color(#254117);
color from = color(#F0EBD4);
color to = color(#5A4A42);
color[] layer_colors = new color[6];
color normal_text_color = color(#FFFC17);
color hover_text_color = color(#FBB917);
color hover_icon_color = color(#7E2217);
// color icon_stroke_color = color(#7E2217);

color ans_qs_color = color(#F62217);
color ask_qs_color = color(#348781);

color egghead_from = color(#FFFC17);
color egghead_to = color(#F76541);

// color egghead_normal_color = color(#FEFEFE);
// color egghead_hover_color = color(#FFFC17);
// color egghead_normal_color = color(#5A4A42);
color egghead_normal_color = color(	#7F5A58);
color egghead_normal_color = color(	#357EC7);
color egghead_normal_color = color(	#25587E);
color egghead_hover_color = color(#A55A3F);

color[] egghead_colors = new color[4];
String[] titles = new String[4];

// setup() 
void setup() {
	size(940, 820);
	frameRate(30);
	titles[0] = "Newbie";
	titles[1] = "Educated";
	titles[2] = "Master";
	titles[3] = "Professor";
	for (int k = 0; k < 6; k++) {
		layer_colors[k] = lerpColor(from, to, 0.35*0.2 * k);
	}
	egghead_colors[0] = color(#FEFEFE);
	egghead_colors[1] = color(#5CB3FF);
	egghead_colors[2] = color(#F9B7FF);
	egghead_colors[3] = color(#FFFC17);
	myself = new Egghead(my_name, my_icon_url);
	myself.load_image();
	center_x = width / 2;
	center_y = 400;
	myself.x = center_x;
	myself.y = center_y;

	int r = floor((my_wealth - min_wealth) * 4.0 / (max_wealth - min_wealth));
	if (r == 4) r = 3;
	myself.icon_color = egghead_colors[r];
	myself.current_icon_color = egghead_normal_color;
	myself.current_text_color = egghead_normal_color;

	eggheads = new ArrayList();

	$.getJSON(json_network_url, function(data){
		$.each(data, function(i, egghead){
			Egghead new_egghead = new Egghead(egghead.name, egghead.icon_url);	
			new_egghead.profile_url = egghead.profile_url;
			new_egghead.ask_url = egghead.ask_url;
			new_egghead.go_url = egghead.go_url;
			new_egghead.wealth = egghead.wealth;
			int max_width = 0;
			int qwidth = 0;
			$.each(egghead.ans_qs, function(i, q){
				new_egghead.ans_qs.add(new Question(q.title, q.link));
				qwidth = font.width(q.title) * font_size;
				if (qwidth > max_width) max_width = qwidth;
			});
			new_egghead.answer_count = new_egghead.ans_qs.size();
			$.each(egghead.ask_qs, function(i, q){
				new_egghead.ask_qs.add(new Question(q.title, q.link));
				qwidth = font.width(q.title) * font_size;
				if (qwidth > max_width) max_width = qwidth;
			});
			new_egghead.question_count = new_egghead.ask_qs.size();
			new_egghead.qbox_width = max_width + 10;
			new_egghead.link_count = new_egghead.question_count + new_egghead.answer_count;
			if (new_egghead.link_count > max_link) {
				max_link = new_egghead.link_count;
			}
			new_egghead.load_image();
			eggheads.add(new_egghead);
		});
		num_egghead = eggheads.size();
		int layer_width = ceil(max_link * 1.0 / 4.0);
		if (num_egghead > 0) {
			for (int k = 0; k < eggheads.size(); k++ ) {
				float theta = k * TWO_PI / num_egghead;
				eggheads[k].theta = theta;
				int layer = 5 - ceil(1.0 * eggheads[k].link_count / layer_width); 
				float radius = layer * 72 + 36;
				eggheads[k].radius = radius;
				eggheads[k].x = center_x + cos(theta) * radius;
				eggheads[k].x0 = eggheads[k].x;
				eggheads[k].y = center_y - sin(theta) * radius;
				eggheads[k].y0 = eggheads[k].y;
				int r = floor((eggheads[k].wealth - min_wealth) * 4.0 / (max_wealth - min_wealth));
				if (r == 4) r = 3;
				eggheads[k].icon_color = egghead_colors[r];
				eggheads[k].current_icon_color = egghead_normal_color;
				eggheads[k].current_text_color = egghead_normal_color;
			}
		}
	});
}

// draw()
void draw(){
	// background(#5E767E);
	background(#FCFEFD);
	fill(layer_colors[0]);
	// ellipse(center_x, center_y, 800, 800);
	noStroke();
	roundedCorners(center_x-450, center_y-400,900,800, 20);
	noStroke();
	for (int k = 0; k < 5; k++) {
		fill(layer_colors[k + 1]);
		ellipse(center_x, center_y, 720 - k * 144, 720 - k * 144);
	}
	// draw_legend();
	forEggheads("move");
	forEggheads("render");
	forEggheads("render_questions");
	forEggheads("buttons");
	myself.render();
}

void draw_legend() {
	fill(#FFFFFF);
	text("Wealth gradient", 65, 650);
	for (int k = 0; k < 4; k++) {
		fill(egghead_colors[k]);
		rect(80, 20*k+680, 50, 20);
		text(titles[k], 135, 680 + 20 * k);
	}
}

// l - an objects storing links -> (x, y, font-size, href, anchor, color, hover color)
Object l={
	new alink(5, 0, 20,"http://www.dafont.com/champagne-limousines.font","Champagne & Limousines",#aa0088,#ff00aa),
	new alink(5, 38, 20,"http://processingjs.org","Processing.js",#aa0088,#ff00aa),
	new alink(5, 72, 20,"http://news.ycombinator.com/","Hacker News",#aa0088,#ff00aa),            
	new alink(5, 104, 20,"http://hascanvas.com","HasCanvas",#aa0088,#ff00aa)
};


void forLinks(mode){
	for(int i=0;i < l.length;i++){
		t = l[i];
		switch(mode){
			case "render":t.render();break;
			case "detect":
				mouseX > t.x &&   
				mouseY > t.y &&
				mouseY < t.y+t.size &&
				mouseX < t.x+t.anchorWidth?
				t.rollOver():
				t.rollOut();
				break;
			case "clicks":t.mouseOver?t.clicked():t.unclicked();
		}
	}
}

void forEggheads(mode){
	for(int i = 0;i < eggheads.size(); i++){
		t = eggheads.get(i);
		switch(mode){
			case "render":t.render();break;
			case "move":t.move();break;
			case "buttons":t.buttons();break;
			case "render_questions": t.render_questions(); break;
			case "detect": t.detect(); break;
			case "clicks": t.check_click(); break;
		}
	}
}

void mouseMoved(){forEggheads("detect");}
void mouseClicked(){forEggheads("clicks");}

class Question{
	String title;
	String question_link;
	Question(String tt, String ql) {
		title = tt;
		question_link = ql;
	}
}

class Egghead{
	// Member variables
	String name, img_url, go_url, profile_url, ask_url;
	PImage icon;
	int answer_count, question_count, link_count, qbox_width;
	int wealth;
	float x, x0, y, y0, name_width, label_width, theta, radius;
	ArrayList ans_qs, ask_qs;
	boolean mouseOver;
	boolean highlighted = false;
	color current_text_color = normal_text_color;
	color icon_color;
	color current_icon_color;
	float dx, dy;
	boolean move_right = true; 
	boolean move_up = true;
	boolean mouseOver_ask = false;
	boolean mouseOver_go = false;
	boolean mouseOver_profile = false;

	// Member methods
	Egghead (String nm, String iu) {
		name = nm;
		name_width = font.width(name) * font_size;
		label_width = max(icon_side, name_width + 20);
		img_url = iu;
		ans_qs = new ArrayList();
		ask_qs = new ArrayList();
		dx = random(0.1, 0.5);
		dy = random(0.1, 0.5);
	}
	void load_image (){
		icon = loadImage(img_url);	
	}
	void detect() {
		(abs(mouseX - x) < icon_side/2) && (abs(mouseY-y) < icon_side/2) ?
		rollOver():
		rollOut();
		if (highlighted) {
			mouseOver_ask = ((mouseX>x-icon_radius*3) && (mouseX<x-icon_radius) && (mouseY>y-icon_side/2-24) && (mouseY<y-icon_side/2));
			mouseOver_go = ((mouseX>x-icon_radius) && (mouseX<x+icon_radius) && (mouseY>y-icon_side/2-24) && (mouseY<y-icon_side/2));
			mouseOver_profile = ((mouseX>x+icon_radius) && (mouseX<x+3*icon_radius) && (mouseY>y-icon_side/2-24) && (mouseY<y-icon_side/2));
			if (mouseOver_ask || mouseOver_go || mouseOver_profile ) {
				cursor("pointer");
			}
			else {
				cursor("auto");
			}
		}
	}
	void check_click() {
		if (mouseOver) {
			clicked();
		}
		else if (highlighted){
			if (mouseOver_ask) { link(ask_url); }
			else if (mouseOver_go) { link(go_url); }
			else if (mouseOver_profile) { link(profile_url); }
			else { unclicked(); }
		}
		else {
			unclicked();
		}
	}
	void move() {
		if (move_right) {
			x += dx;
			if (x > x0 + 10) move_right = false;
		} else {
			x -= dx;
			if (x < x0 - 10) move_right = true;
		}
		if (move_up) {
			y -= dy;
			if (y < y0 - 10) move_up = false;
		} else {
			y += dy;
			if (y > y0 + 10) move_up = true;
		}
	}
	void render() {
		noFill();	
		strokeCap(ROUND);
		strokeJoin(ROUND);
		if (name != my_name) {	
			pushMatrix();
				translate(center_x, center_y);
				rotate(-theta);
				float dist = radius - 10 - 2 * icon_radius;
				float gap = 15;
				if (answer_count > 0) {
					strokeWeight(answer_count*2);
					stroke(ans_qs_color);
					beginShape();
						curveVertex(icon_radius + 5, 0);
						curveVertex(icon_radius + 5, 0);
						curveVertex(icon_radius + 5 + dist/8, gap*sin(PI/8));
						curveVertex(icon_radius + 5 + dist/4, gap*sin(PI/4));
						curveVertex(icon_radius + 5 + 3*dist/8, gap*sin(3*PI/8));
						curveVertex(icon_radius + 5 + dist/2, gap);
						curveVertex(icon_radius + 5 + 5*dist/8, gap*sin(3*PI/8));
						curveVertex(icon_radius + 5 + 3*dist/4, gap*sin(PI/4));
						curveVertex(icon_radius + 5 + 7*dist/8, gap*sin(PI/8));
						curveVertex(radius - 5 - icon_radius, 0);
						curveVertex(radius - 5 - icon_radius, 0);
					endShape();
				}
				if (question_count > 0) {
					strokeWeight(question_count*2);
					stroke(ask_qs_color);
					beginShape();
						curveVertex(icon_radius + 5, 0);
						curveVertex(icon_radius + 5, 0);
						curveVertex(icon_radius + 5 + dist/8, -gap*sin(PI/8));
						curveVertex(icon_radius + 5 + dist/4, -gap*sin(PI/4));
						curveVertex(icon_radius + 5 + 3*dist/8, -gap*sin(3*PI/8));
						curveVertex(icon_radius + 5 + dist/2, -gap);
						curveVertex(icon_radius + 5 + 5*dist/8, -gap*sin(3*PI/8));
						curveVertex(icon_radius + 5 + 3*dist/4, -gap*sin(PI/4));
						curveVertex(icon_radius + 5 + 7*dist/8, -gap*sin(PI/8));
						curveVertex(radius - 5 - icon_radius, 0);
						curveVertex(radius - 5 - icon_radius, 0);
					endShape();
				}
			popMatrix();
		}
		strokeWeight(2);
		stroke(current_icon_color);
		fill(current_icon_color);
		image(icon, x - icon_size / 2, y - icon_size / 2);
		noFill();
		roundedCorners(x-icon_side/2, y-icon_side/2, icon_side, icon_side, 5);
		// ellipse(x, y, 2 * icon_radius, 2 * icon_radius);
		fill(current_icon_color);
		// roundedCorners(x-label_width/2, y-icon_side/2-15, label_width, 20, 5);
		textFont(font, font_size);
		fill(current_icon_color);
		text(name, x - name_width / 2, y + icon_side/2+4);
	}
	void rollOver() {
		if (!mouseOver) {      
			mouseOver = true;
			cursor("pointer");
			// current_text_color = hover_text_color;
			current_icon_color = egghead_hover_color;
			render();
		}
	}

	void rollOut() {
		if (mouseOver) {
			mouseOver=false;
			cursor("auto");
			// current_text_color = normal_text_color;
			current_icon_color = egghead_normal_color;
			render();
		}
	}

	void render_questions() {
		if (mouseOver || highlighted) {
			strokeWeight(3);
			stroke(#157DEC);
			fill(#FFFFFF);
			float left_x = x + qbox_width > width ? width - qbox_width : x;
			if (answer_count > 0) {
				stroke(ans_qs_color);
				roundedCorners(left_x, y, qbox_width, 20 * answer_count + 5, 10);
				fill(ans_qs_color);
				for (int k = 0; k < ans_qs.size(); k++) {
					text(ans_qs.get(k).title, left_x + 5, y + 20 * k + 3);
				}
			}
			if (question_count > 0) {
				stroke(ask_qs_color);
				fill(#FFFFFF);
				roundedCorners(left_x, 8+y + 20 * answer_count, qbox_width, 20 * question_count + 5, 10);
				fill(ask_qs_color);
				for (int k = 0; k < question_count; k++) {
					text(ask_qs.get(k).title, left_x + 5, 11+y + 20 * answer_count + 20 * k);
				}
			}
		}
	}
	void buttons(){
		if (highlighted) {
			color stroke_color;
			color fill_color;
			stroke_color = mouseOver_ask?color(#157DEC):color(#810541);
			fill_color = mouseOver_ask?color(#153E7E):color(#800517);
			stroke(stroke_color);
			fill(fill_color);
			roundedCorners(x-icon_radius*3, y-icon_side/2-24, 2*icon_radius, 20, 10);
			stroke_color = mouseOver_go?color(#157DEC):color(#810541);
			fill_color = mouseOver_go?color(#153E7E):color(#800517);
			stroke(stroke_color);
			fill(fill_color);
			roundedCorners(x-icon_radius, y-icon_side/2-24, 2*icon_radius, 20, 10);
			stroke_color = mouseOver_profile?color(#157DEC):color(#810541);
			fill_color = mouseOver_profile?color(#153E7E):color(#800517);
			stroke(stroke_color);
			fill(fill_color);
			roundedCorners(x+icon_radius, y-icon_side/2-24, 2*icon_radius, 20, 10);
			fill(#FFFFFF);
			text("Ask", x-icon_radius*3 + 15, y-icon_side/2-24);
			text("Go!", x-icon_radius + 15, y-icon_side/2-24);
			text("More", x+icon_radius + 10, y-icon_side/2-24);
		}
	}
	void clicked() {
		if (!highlighted) {
			highlighted = true;
		}
	}
	void unclicked() {
		if (highlighted) {
			highlighted = false;
		}
	}
	void randomize() {
		x += random(-0.5, 0.5);
		y += random(-0.5, 0.5);
	}
}

class alink{
	boolean mouseOver;
	color current_col;
	float anchorWidth;
	alink(float x, float y, float size, String href,
		String anchor, Color text_col, Color hover_col)
	{
		href = href;    
		anchor = anchor;    
		this.size = size;
		this.x = x, this.y = y;
		text_col=text_col;
		hover_col=hover_col;
		current_col=text_col;
		mouseOver=false;    
	}
	void render() {
		anchorWidth = font.width(anchor) * size;    
		// clear(x,y,anchorWidth,size+4);
		noFill();
		strokeWeight(2);
		stroke(#5CB3FF);
		roundedCorners(x, y, 200, 100, 15);
		textFont(font,size);
		fill(current_col);
		mouseOver?rect(x,y+size+2,anchorWidth,1):0;
		text(anchor,x,y);    
	}
	void rollOver() {
		if (!mouseOver) {      
			mouseOver=true;
			cursor("pointer");
			current_col=hover_col;
			render();
		}
	}

	void rollOut() {
		if(mouseOver) {
			mouseOver=false;
			cursor("auto");
			current_col=text_col;
			render();
		}
	}

	void clicked() {
		link(href);
	}
}
void roundedCorners(int left, int top, int width, int height, int roundness)   {  
	beginShape();
	vertex(left + roundness, top);  
	vertex(left + width - roundness, top);
	bezierVertex(left + width - roundness, top, 
		left + width, top, left + width, top + roundness);  
	vertex(left + width, top + roundness);  
	vertex(left + width, top + height - roundness);  
	bezierVertex(left + width, top + height - roundness,  
		left + width, top + height, left + width - roundness, top + height);  
	vertex(left + width - roundness, top + height);  
	vertex(left + roundness, top + height);
	bezierVertex(left + roundness, top + height,  
		left, top + height, left, top + height - roundness);  
	vertex(left, top + height - roundness);  
	vertex(left, top + roundness);  
	bezierVertex(left, top + roundness,  
		left, top, left + roundness, top);          
	endShape();  
}  
