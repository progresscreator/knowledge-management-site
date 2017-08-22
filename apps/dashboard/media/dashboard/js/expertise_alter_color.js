float font_size = 13;
PFont font=loadFont(font_url);
float icon_size = 50;
float icon_radius = 24;
float icon_side = 50;

ArrayList tags;
ArrayList eggheads;
ArrayList questions;

color from = color(#A55A3F);
color to = color(#5A4A42);
int max_tag_count = 0;
int min_tag_count = 10000;
int font_min_size = 14;
int font_max_size = 36;

int tag_panel_width = 695;
int egghead_panel_width = 245;
int bounary_weight = 2;

color icon_text_color_normal = color(#151B54);
color icon_stroke_color = color(#488AC7);
color hover_text_color = color(#800517);
color icon_color_normal = color(#FFFFFF);
color hover_icon_color = color(#7E2217);
color hover_question_color = color(#461B7E);
color marked_color = color(#3090C7);

color tag_normal_text_color = color(#FFFFFF);
color tag_hover_text_color = color(#ECE5B6);
color tag_hover_background_color = color(#25587E);
color tag_linked_color = color(#348781);
color question_normal_color = color(#5A4A42);
color question_hover_color = color(#A55A3F);

color egghead_from = color(#b4f3fd);
color egghead_to = color(#14134e);

color egghead_normal_color = color(#5A4A42);
color egghead_hover_color = color(#A55A3F);

color[] egghead_colors = new color[4];
float total_energy = 100;
float ts = 0.1;
float damping = 0.7;
float coeff_rep = 10000;
float spring = 0.1;
float wall_spring = 0.05;
float cushion = 30;

int iter = 0;
// setup() 
void setup() {
	size(940, 720);
	frameRate(20);
	tags = new ArrayList();
	eggheads = new ArrayList();
	questions = new ArrayList();
	egghead_colors[0] = color(#FEFEFE);
	egghead_colors[1] = color(#F9B7FF);
	egghead_colors[2] = color(#5CB3FF);
	egghead_colors[3] = color(#FFFC17);
	$.getJSON(json_expertise_url, function(data){
		$.each(data.questions, function(i, question) {
			questions.add(new Question(i, question.question_id, question.title, question.link));
		});
		$.each(data.tags, function(i, tag){
			Tag new_tag = new Tag(i, tag.name, tag.count, tag.tag_id);
			tags.add(new_tag);
			if (tag.count > max_tag_count) max_tag_count = tag.count;
			if (tag.count < min_tag_count) min_tag_count = tag.count;
			$.each(tag.linked_tags, function(i, linked_tag) {
				new_tag.linked_tags.add(new LinkedTag(linked_tag.tag_id, linked_tag.count));
			});
			$.each(tag.experts, function(i, linked_expert) {
				new_tag.linked_experts.add(new LinkedExpert(linked_expert.user_id, linked_expert.count));
			});
			$.each(tag.linked_questions, function(i, question_id) {
				for (int k = 0; k < questions.size(); k++) {
					if (questions.get(k).question_id == question_id) {
						new_tag.linked_question_indexes.add(k);
						break;
					}
				}
			});
		});
		$.each(data.eggheads, function(i, egghead) {
			Egghead new_egghead = new Egghead(i, egghead.user_id, egghead.name, egghead.img_url, egghead.profile_url, egghead.wealth);
			new_egghead.load_image();
			eggheads.add(new_egghead);
		});
		forTags("initialize");
	});
}

void draw() {
	background("white");
	stroke(#5A4A42);
	strokeWeight(bounary_weight*2);
	fill(#F0EBD4);
	roundedCorners(bounary_weight, bounary_weight, 
		tag_panel_width - 1 * bounary_weight, tag_panel_width, 10);
	roundedCorners(tag_panel_width + bounary_weight, bounary_weight, 
		egghead_panel_width - 2 * bounary_weight, tag_panel_width / 2 + 40 - bounary_weight, 10);
	roundedCorners(tag_panel_width + bounary_weight, 2*bounary_weight + tag_panel_width/2 + 40, 
		egghead_panel_width - 2 * bounary_weight, tag_panel_width / 2 - 40 - bounary_weight, 10);
	/*
	if (!frozen()) {
		forTags("collide");
		forTags("move");
	}
	*/
	if ((total_energy > 12) && (iter <= 500) && (tags.size() > 0)){
		force_directed_layout();
		forTags("move");
	}
	forTags("render");
}

boolean frozen() {
	for (int k = 0; k < tags.size(); k++) {
		if (tags.get(k).highlighted) {
			return true;
		}
	}
	return false;
}

void force_directed_layout() {
	float energy = 0;
	for(int k = 0; k < tags.size(); k++) {
		float force_x = 0;
		float force_y = 0;
		for (int l = 0; l < tags.size(); l++) {
			Force fr = tags[k].repulsion(tags[l]);
			Force fw = tags[k].wall();
			force_x += fr.fx;
			force_x += fw.fx;
			force_y += fr.fy;
			force_y += fw.fy;
		}
		Force fa = tags[k].attraction();
		force_x += fa.fx;
		force_y += fa.fy;
		tags[k].dx = (tags[k].dx + ts * force_x / tags[k].count) * damping;
		tags[k].dy = (tags[k].dy + ts * force_y / tags[k].count) * damping;
		energy += sq(tags[k].dx) + sq(tags[k].dy);
	}
	total_energy = energy;
	iter += 1;
	// console.log("Iter " + iter + " - total energy: " + total_energy);
}

void forTags(mode){
	for(int i = 0;i < tags.size(); i++){
		Tag t = tags.get(i);
		switch(mode){
			case "render":t.render();break;
			case "collide":t.collide();break;
			case "move":t.move();break;
			case "initialize":t.initialize();break;
			case "buttons":t.buttons();break;
			case "render_questions": t.render_questions(); break;
			case "detect": t.detect(); break;
			case "clicks_down": t.check_click_down(); break;
			case "clicks_up": t.check_click_up(); break;
		}
	}
}
void forEggheads(mode){
	for(int i = 0;i < eggheads.size(); i++){
		Egghead e = eggheads.get(i);
		switch(mode){
			case "detect": e.detect(); break;
			case "clicks": e.check_click(); break;
		}
	}
}
void forQuestions(mode){
	for(int i = 0;i < questions.size(); i++){
		Question q = questions.get(i);
		switch(mode){
			case "detect": q.detect(); break;
			case "clicks": q.check_click(); break;
		}
	}
}
void mouseMoved() {
	forTags("detect");
	forEggheads("detect");
	forQuestions("detect");
}
void mouseClicked() {
	forTags("clicks_up");
	forTags("clicks_down");
	forEggheads("clicks");
	forQuestions("clicks");
}

class LinkedTag {
	int tag_id, count, tag_index = -1;
	LinkedTag(int tid, int c) {
		tag_id = tid;
		count = c;
	}
}
class LinkedExpert {
	int expert_id, count, egghead_index = -1;
	LinkedExpert(int eid, int c) {
		expert_id = eid;
		count = c;
	}
}

class Force{
	float fx, fy;
	Force (float x, float y) {
		fx = x;
		fy = y;
	}
}

class Tag{
	String name;
	int index, count, tag_id, t_font_size;
	float x, y, t_wid, t_hei, dx, dy;
	color self_color, current_background_color, current_text_color;
	boolean mouseOver;
	boolean highlighted;

	ArrayList linked_experts;
	ArrayList linked_tags;
	ArrayList linked_question_indexes;

	Tag(int i, String n, int c, int tid) {
		index = i;
		name = n;
		count = c;
		tag_id = tid;

		linked_experts = new ArrayList();
		linked_tags = new ArrayList();
		linked_question_indexes = new ArrayList();
	}
	Force repulsion(Tag t) {
		if (tag_id == t.tag_id) return new Force(0, 0);
		float dist_sq = max(1, sq(x+t_wid/2-t.x-t.t_wid/2) + sq(y+t_hei/2-t.y-t.t_hei/2));
		float dist = max(1e-6, sqrt(dist_sq));
		float force = 1.0 * count * t.count / dist_sq * coeff_rep;
		float fx = (x+t_wid/2-t.x-t.t_wid/2) / dist * force;
		float fy = (y+t_hei/2-t.y-t.t_hei/2) / dist * force;
		if (overlap(t)) {
			fx *= 5;
			fy *= 5;
		}
		return new Force(fx, fy);
	}
	Force attraction() {
		float ft_x = 0;
		float ft_y = 0;
		for (int k = 0; k < linked_tags.size(); k++) {
			Tag t = tags.get(linked_tags[k].tag_index);
			float dist_sq = sq(x - t.x) + sq(y - t.y);
			float dist = max(1e-6, sqrt(dist_sq));
			float force = 1.0 * linked_tags[k].count * dist * spring;
			float ft_x = (t.x - x) / dist * force;
			float ft_y = (t.y - y) / dist * force;
		}
		return new Force(ft_x, ft_y);
	}
	Force wall() {
		float f_x = 0;
		float f_y = 0;
		float delta_x =  x + t_wid - (tag_panel_width - 2 * bounary_weight - cushion);
		if (delta_x > 0) {
			f_x = - delta_x * wall_spring;
		}
		delta_x = 2 * bounary_weight + cushion - x;
		if (delta_x > 0) {
			f_x = delta_x * wall_spring;
		}
		float delta_y = 2 * bounary_weight + cushion - y;
		if (delta_y > 0) {
			f_y = delta_y * wall_spring;
		}
		delta_y = y + t_hei - (tag_panel_width - bounary_weight/2 - cushion);
		if (delta_y > 0) {
			f_y = - delta_y * wall_spring;
		}
		return new Force(f_x, f_y);
	}
	void check_click_down() {
		if (mouseOver) {
			highlighted = true;
			/*
			for (int k = 0; k < linked_tags.size(); k++) {
				tag = tags.get(linked_tags.get(k).tag_index);
				tag.current_background_color = tag.self_color;
			}
			*/
			for (int k = 0; k < linked_experts.size(); k++) {
				int m = linked_experts[k].egghead_index;
				eggheads.get(m).displayed = true;
			}
			for (int k = 0; k < linked_question_indexes.size(); k++) {
				Question q = questions.get(linked_question_indexes.get(k));
				q.displayed = true;
			}
		}
	}
	void check_click_up() {
		if (!mouseOver) {
			if (highlighted) {
				for (int k = 0; k < linked_experts.size(); k++) {
					int m = linked_experts[k].egghead_index;
					eggheads.get(m).displayed = false;
				}
				for (int k = 0; k < linked_question_indexes.size(); k++) {
					Question q = questions.get(linked_question_indexes.get(k));
					q.displayed = false;
				}
				highlighted = false;
			}
			current_background_color = self_color;
			current_text_color = tag_normal_text_color;
		}
	}
	boolean overlap(Tag t) {
		if ((x + t_wid < t.x) ||	
			(x > t.x + t.t_wid) ||
			(y > t.y + t.t_hei) ||
			(y + t_hei < t.y))
			return false;
		return true;
	}
	void collide() {
		for (int k = index + 1; k < tags.size(); k++) {
			Tag t = tags.get(k);
			float spring = 0.005;
			if (overlap(t)) {
				float x_center_dist = x + t_wid/2 - (t.x + t.t_wid/2);
				float x_delta = t_wid/2 + t.t_wid/2 - abs(x_center_dist);
				float ax = (x_center_dist > 0)? x_delta * spring : -x_delta * spring;

				float y_center_dist = y + t_hei/2 - (t.y + t.t_hei/2);
				float y_delta = t_hei/2 + t.t_hei/2 - abs(y_center_dist);
				float ay = (y_center_dist > 0)? y_delta * spring : -y_delta * spring;

				dx += ax;
				t.dx -= ax;
				x += x_delta / 2;
				t.x -= x_delta / 2;

				dy += ay;
				t.dy -= ay;
				y += y_delta / 2;
				t.y -= y_delta / 2;
			}
		}
	}
	void move() {
		x += dx;
		y += dy;
		if (x + t_wid > tag_panel_width - 2 * bounary_weight) {
			dx *= -1;
			x = tag_panel_width - t_wid - 2 * bounary_weight;
		}
		if (x < 2 * bounary_weight) {
			dx *= -1;
			x = 2 * bounary_weight;
		}
		if (y < 2 * bounary_weight) {
			dy *= -1;
			y = 2 * bounary_weight;
		}
		if (y + t_hei > tag_panel_width - bounary_weight/2) {
			dy *= -1;
			y = tag_panel_width - t_hei - bounary_weight/2
		}
	}
	void initialize() {
		if (max_tag_count == min_tag_count) {
			self_color = from;
			t_font_size = font_min_size;
		} else {
			self_color = lerpColor(from, to,
				0.2 * (count - min_tag_count) / (max_tag_count - min_tag_count));
			t_font_size = round(font_min_size + (count - min_tag_count) * 1.0 / 
				(max_tag_count - min_tag_count) * (font_max_size - font_min_size));
		}
		current_background_color = self_color;
		// current_background_color = color(#FFFFFF);
		// stroke(#ECE5B6);
		current_text_color = tag_normal_text_color;
		t_wid = font.width(name) * t_font_size + 16;
		t_hei = t_font_size + 6;
		x = random(0, tag_panel_width - t_wid);
		y = random(0, tag_panel_width - t_hei);

		// dx = (random(-1, 1) > 0)? 0.4 : -0.4;
		// dy = (random(-1, 1) > 0)? 0.6 : -0.6;
		dx = 0;
		dy = 0;	
		for (int k = 0; k < linked_tags.size(); k++) {
			for (int l = 0; l < tags.size(); l++) {
				if (tags.get(l).tag_id == linked_tags.get(k).tag_id) {
					linked_tags.get(k).tag_index = l;
					break;
				}
			}
		}
		for (int k = 0; k < linked_experts.size(); k++) {
			for (int l = 0; l < eggheads.size(); l++) {
				if (eggheads.get(l).user_id == linked_experts.get(k).expert_id) {
					linked_experts.get(k).egghead_index = l;
					break;
				}
			}
		}
	}
	boolean has_egghead_id(int id) {
		for (int k = 0; k < linked_experts.size(); k++) {
			if (linked_experts.get(k).expert_id == id) return true;
		}
		return false;
	}
	void render() {
		if (mouseOver || highlighted) {
			for (int k = 0; k < linked_tags.size(); k++) {
				Tag tag = tags.get(linked_tags.get(k).tag_index);
				strokeWeight(2 * linked_tags.get(k).count);
				stroke(#306EFF);
				tag.current_background_color = tag_linked_color;
				tag.current_text_color = tag_hover_text_color;
				line(x + t_wid/2, y+t_hei/2, tag.x+tag.t_wid/2, tag.y+tag.t_hei/2);
			}
			if (!(!highlighted && frozen())) {
				for (int k = 0; k < linked_experts.size(); k++) {
					int m = linked_experts[k].egghead_index;
					eggheads.get(m).y = k * 75 + 40;
					eggheads.get(m).temp_count = linked_experts[k].count;
					eggheads.get(m).render();
				}
				for (int k = 0; k < linked_question_indexes.size(); k++) {
					Question q = questions.get(linked_question_indexes.get(k));
					q.y = k * 20 + 2*bounary_weight + tag_panel_width/2 + 50;
					q.render();
				}
			}
		}
		else {
			for (int k = 0; k < linked_tags.size(); k++) {
				Tag tag = tags.get(linked_tags.get(k).tag_index);
				if (tag.index > index) {
					strokeWeight(2 * linked_tags.get(k).count);
					stroke("#87AFC7");
					line(x + t_wid/2, y+t_hei/2, tag.x+tag.t_wid/2, tag.y+tag.t_hei/2);
				}
			}
		}
		textFont(font, t_font_size);
		strokeWeight(2);
		// stroke(#348781);
		noStroke();
		fill(current_background_color);
		roundedCorners(x, y, t_wid, t_hei, 8);
		fill(current_text_color);
		text(name, x+8, y);
	}
	void detect() {
		((mouseX>x) && (mouseX<x+t_wid) && (mouseY>y) && (mouseY<y+t_hei))?
		rollOver():
		rollOut();
	}
	void rollOver() {
		if (!mouseOver) {      
			mouseOver = true;
			cursor("pointer");
			current_background_color = tag_hover_background_color;
			current_text_color = tag_hover_text_color;
			render();
		}
	}
	void rollOut() {
		if (mouseOver) {
			mouseOver=false;
			cursor("auto");
			if (!highlighted) {
				current_background_color = self_color;
				current_text_color = tag_normal_text_color;
			}
			render();
			for (int k = 0; k < linked_tags.size(); k++) {
				tag = tags.get(linked_tags.get(k).tag_index);
				tag.current_background_color = tag.self_color;
				tag.current_text_color = tag_normal_text_color;
			}
		}
	}
}

class Egghead{
	// Member variables
	String name, img_url, profile_url;
	int user_id, index, temp_count = 0;
	PImage icon;
	float x, y, name_width;
	color current_stroke_color;
	boolean displayed = false;
	boolean mouseOver = false;
	int wealth;

	color current_icon_color;
	color current_text_color;
	color icon_color;
	Egghead (int ind, int uid, String nm, String iu, String purl, int wth) {
		index = ind;
		user_id = uid;
		name = nm;
		name_width = font.width(name) * font_size;
		img_url = iu;
		profile_url = purl;
		wealth = wth;
		x = tag_panel_width + egghead_panel_width / 2 + bounary_weight;
		current_text_color = egghead_normal_color;
		current_icon_color = egghead_normal_color;
	}
	void load_image (){
		icon = loadImage(img_url);	
	}
	void detect() {
		if (displayed) {
			(abs(mouseX-x)<icon_side/2) && (abs(mouseY-y)<icon_side/2) ?
			rollOver():
			rollOut();
		}
	}
	void check_click() {
		if (mouseOver) link(profile_url);
	}
	void render() {
		image(icon, x - icon_size / 2, y - icon_size / 2);
		strokeWeight(2);
		stroke(current_icon_color);
		noFill();
		roundedCorners(x-icon_side/2, y-icon_side/2, icon_side, icon_side, 5);
		strokeWeight(2);
		stroke(#7AA5B3);
		fill(#F62217);
		ellipse(x + icon_side*0.48, y - 0.42*icon_side, 18, 18);
		fill(current_text_color);
		textFont(font, font_size);
		text(name, x - name_width / 2, y + icon_side/2 + 3);
		fill(#FEFEFE);
		text(str(temp_count), x + icon_side*0.48 - font.width(str(temp_count))*font_size/2, 
			y - 0.60 * icon_side);
	}
	void rollOver() {
		if (!mouseOver) {      
			mouseOver = true;
			cursor("pointer");
			current_text_color = egghead_hover_color;
			current_icon_color = egghead_hover_color;
			render();
			for (int k = 0; k < tags.size(); k++) {
				Tag t = tags.get(k);
				if (t.has_egghead_id(user_id) && (t.current_background_color==t.self_color)) {
					t.current_background_color = marked_color;
					t.current_text_color = tag_hover_text_color;
				}
			}
		}
	}

	void rollOut() {
		if (mouseOver) {
			mouseOver=false;
			cursor("auto");
			current_text_color = egghead_normal_color;
			current_icon_color = egghead_normal_color;
			render();
			for (int k = 0; k < tags.size(); k++) {
				Tag t = tags.get(k);
				if (t.has_egghead_id(user_id) && (t.current_background_color == marked_color)) {
					t.current_background_color = t.self_color;
					t.current_text_color = tag_normal_text_color;
				}
			}
		}
	}
}

class Question{
	// Member variables
	String title, question_link;
	int question_id, index, title_width;
	float x, y, name_width;
	boolean displayed = false, mouseOver = false;
	color current_text_color;
	Question (int ind, int qid, String tt, String li) {
		index = ind;
		question_id = qid;

		if (tt.length() > 35) {
			title = tt.substring(0, 34) + "...";
		}
		else {
			title = tt;
		}

		question_link = li;
		title_width = font.width(title) * font_size;
		x = tag_panel_width + bounary_weight + 6;
		current_text_color = question_normal_color;
	}
	void detect() {
		if (displayed) {
			((mouseX>x) && (mouseX<x+title_width) && (mouseY>y) && (mouseY<y+20))?
			rollOver():
			rollOut();
		}
	}
	void check_click() {
		if (mouseOver) link(question_link);
	}
	void render() {
		fill(current_text_color);
		text(title, x, y);
	}
	void rollOver() {
		if (!mouseOver) {      
			mouseOver = true;
			cursor("pointer");
			current_text_color = question_hover_color;
			// render();
		}
	}
	void rollOut() {
		if (mouseOver) {
			mouseOver=false;
			cursor("auto");
			current_text_color = question_normal_color;
			// render();
		}
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
