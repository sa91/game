#include <iostream>
#include <cmath>
#include <fstream>
#include <vector>

#include <glad/glad.h>
#include <GLFW/glfw3.h>

#define GLM_FORCE_RADIANS
#include <glm/glm.hpp>
#include <glm/gtx/transform.hpp>
#include <glm/gtc/matrix_transform.hpp>

using namespace std;

struct VAO {
    GLuint VertexArrayID;
    GLuint VertexBuffer;
    GLuint ColorBuffer;

    GLenum PrimitiveMode;
    GLenum FillMode;
    int NumVertices;
};
typedef struct VAO VAO;

struct GLMatrices {
	glm::mat4 projection;
	glm::mat4 model;
	glm::mat4 view;
	GLuint MatrixID;
} Matrices;

GLuint programID;

/* Function to load Shaders - Use it as it is */
GLuint LoadShaders(const char * vertex_file_path,const char * fragment_file_path) {

	// Create the shaders
	GLuint VertexShaderID = glCreateShader(GL_VERTEX_SHADER);
	GLuint FragmentShaderID = glCreateShader(GL_FRAGMENT_SHADER);

	// Read the Vertex Shader code from the file
	std::string VertexShaderCode;
	std::ifstream VertexShaderStream(vertex_file_path, std::ios::in);
	if(VertexShaderStream.is_open())
	{
		std::string Line = "";
		while(getline(VertexShaderStream, Line))
			VertexShaderCode += "\n" + Line;
		VertexShaderStream.close();
	}

	// Read the Fragment Shader code from the file
	std::string FragmentShaderCode;
	std::ifstream FragmentShaderStream(fragment_file_path, std::ios::in);
	if(FragmentShaderStream.is_open()){
		std::string Line = "";
		while(getline(FragmentShaderStream, Line))
			FragmentShaderCode += "\n" + Line;
		FragmentShaderStream.close();
	}

	GLint Result = GL_FALSE;
	int InfoLogLength;

	// Compile Vertex Shader
	printf("Compiling shader : %s\n", vertex_file_path);
	char const * VertexSourcePointer = VertexShaderCode.c_str();
	glShaderSource(VertexShaderID, 1, &VertexSourcePointer , NULL);
	glCompileShader(VertexShaderID);

	// Check Vertex Shader
	glGetShaderiv(VertexShaderID, GL_COMPILE_STATUS, &Result);
	glGetShaderiv(VertexShaderID, GL_INFO_LOG_LENGTH, &InfoLogLength);
	std::vector<char> VertexShaderErrorMessage(InfoLogLength);
	glGetShaderInfoLog(VertexShaderID, InfoLogLength, NULL, &VertexShaderErrorMessage[0]);
	fprintf(stdout, "%s\n", &VertexShaderErrorMessage[0]);

	// Compile Fragment Shader
	printf("Compiling shader : %s\n", fragment_file_path);
	char const * FragmentSourcePointer = FragmentShaderCode.c_str();
	glShaderSource(FragmentShaderID, 1, &FragmentSourcePointer , NULL);
	glCompileShader(FragmentShaderID);

	// Check Fragment Shader
	glGetShaderiv(FragmentShaderID, GL_COMPILE_STATUS, &Result);
	glGetShaderiv(FragmentShaderID, GL_INFO_LOG_LENGTH, &InfoLogLength);
	std::vector<char> FragmentShaderErrorMessage(InfoLogLength);
	glGetShaderInfoLog(FragmentShaderID, InfoLogLength, NULL, &FragmentShaderErrorMessage[0]);
	fprintf(stdout, "%s\n", &FragmentShaderErrorMessage[0]);

	// Link the program
	fprintf(stdout, "Linking program\n");
	GLuint ProgramID = glCreateProgram();
	glAttachShader(ProgramID, VertexShaderID);
	glAttachShader(ProgramID, FragmentShaderID);
	glLinkProgram(ProgramID);

	// Check the program
	glGetProgramiv(ProgramID, GL_LINK_STATUS, &Result);
	glGetProgramiv(ProgramID, GL_INFO_LOG_LENGTH, &InfoLogLength);
	std::vector<char> ProgramErrorMessage( max(InfoLogLength, int(1)) );
	glGetProgramInfoLog(ProgramID, InfoLogLength, NULL, &ProgramErrorMessage[0]);
	fprintf(stdout, "%s\n", &ProgramErrorMessage[0]);

	glDeleteShader(VertexShaderID);
	glDeleteShader(FragmentShaderID);

	return ProgramID;
}

static void error_callback(int error, const char* description)
{
    fprintf(stderr, "Error: %s\n", description);
}

void quit(GLFWwindow *window)
{
    glfwDestroyWindow(window);
    glfwTerminate();
    exit(EXIT_SUCCESS);
}


/* Generate VAO, VBOs and return VAO handle */
struct VAO* create3DObject (GLenum primitive_mode, int numVertices, const GLfloat* vertex_buffer_data, const GLfloat* color_buffer_data, GLenum fill_mode=GL_FILL)
{
    struct VAO* vao = new struct VAO;
    vao->PrimitiveMode = primitive_mode;
    vao->NumVertices = numVertices;
    vao->FillMode = fill_mode;

    // Create Vertex Array Object
    // Should be done after CreateWindow and before any other GL calls
    glGenVertexArrays(1, &(vao->VertexArrayID)); // VAO
    glGenBuffers (1, &(vao->VertexBuffer)); // VBO - vertices
    glGenBuffers (1, &(vao->ColorBuffer));  // VBO - colors

    glBindVertexArray (vao->VertexArrayID); // Bind the VAO 
    glBindBuffer (GL_ARRAY_BUFFER, vao->VertexBuffer); // Bind the VBO vertices 
    glBufferData (GL_ARRAY_BUFFER, 3*numVertices*sizeof(GLfloat), vertex_buffer_data, GL_STATIC_DRAW); // Copy the vertices into VBO
    glVertexAttribPointer(
                          0,                  // attribute 0. Vertices
                          3,                  // size (x,y,z)
                          GL_FLOAT,           // type
                          GL_FALSE,           // normalized?
                          0,                  // stride
                          (void*)0            // array buffer offset
                          );

    glBindBuffer (GL_ARRAY_BUFFER, vao->ColorBuffer); // Bind the VBO colors 
    glBufferData (GL_ARRAY_BUFFER, 3*numVertices*sizeof(GLfloat), color_buffer_data, GL_STATIC_DRAW);  // Copy the vertex colors
    glVertexAttribPointer(
                          1,                  // attribute 1. Color
                          3,                  // size (r,g,b)
                          GL_FLOAT,           // type
                          GL_FALSE,           // normalized?
                          0,                  // stride
                          (void*)0            // array buffer offset
                          );

    return vao;
}

/* Generate VAO, VBOs and return VAO handle - Common Color for all vertices */
struct VAO* create3DObject (GLenum primitive_mode, int numVertices, const GLfloat* vertex_buffer_data, const GLfloat red, const GLfloat green, const GLfloat blue, GLenum fill_mode=GL_FILL)
{
    GLfloat* color_buffer_data = new GLfloat [3*numVertices];
    for (int i=0; i<numVertices; i++) {
        color_buffer_data [3*i] = red;
        color_buffer_data [3*i + 1] = green;
        color_buffer_data [3*i + 2] = blue;
    }

    return create3DObject(primitive_mode, numVertices, vertex_buffer_data, color_buffer_data, fill_mode);
}

/* Render the VBOs handled by VAO */
void draw3DObject (struct VAO* vao)
{
    // Change the Fill Mode for this object
    glPolygonMode (GL_FRONT_AND_BACK, vao->FillMode);

    // Bind the VAO to use
    glBindVertexArray (vao->VertexArrayID);

    // Enable Vertex Attribute 0 - 3d Vertices
    glEnableVertexAttribArray(0);
    // Bind the VBO to use
    glBindBuffer(GL_ARRAY_BUFFER, vao->VertexBuffer);

    // Enable Vertex Attribute 1 - Color
    glEnableVertexAttribArray(1);
    // Bind the VBO to use
    glBindBuffer(GL_ARRAY_BUFFER, vao->ColorBuffer);

    // Draw the geometry !
    glDrawArrays(vao->PrimitiveMode, 0, vao->NumVertices); // Starting from vertex 0; 3 vertices total -> 1 triangle
}

/**************************
 * Customizable functions *
 **************************/

float triangle_rot_dir = 1;
float rectangle_rot_dir = 1;
bool triangle_rot_status = true;
bool rectangle_rot_status = true;
float Floor_limit=-2;
typedef struct eye
{
    float x,y,z;
    float ox,oy,oz;
    int state;
}eye;
eye camera;
typedef struct object
{
        struct VAO* sprite;
        float posx,posy,posz;
        float x,y,z;
        float vx,vy,vz;
        float radius;
        float mass;
        float rotation;
        float size;
        bool on_platform;
}object;
object player;
vector <object> flor;
vector <object> obstacle;


void moveTile(object *);
bool checkFloor(object *);
void deleteTiles();
void slideBlock(object *,int);
/* Executed when a regular key is pressed/released/held-down */
/* Prefered for Keyboard events */


/* Executed for character input (like in text boxes) */
void keyboardChar (GLFWwindow* window, unsigned int key)
{
	switch (key) {
		case 'Q':
		case 'q':
            quit(window);
            break;
		default:
			break;
	}
}
void mouseButton (GLFWwindow* window, int button, int action, int mods)
{
    switch (button) {
        case GLFW_MOUSE_BUTTON_LEFT:
            if (action == GLFW_RELEASE)
                triangle_rot_dir *= -1;
            break;
        case GLFW_MOUSE_BUTTON_RIGHT:
            if (action == GLFW_RELEASE) {
                rectangle_rot_dir *= -1;
            }
            break;
        default:
            break;
    }
}
void keyboard (GLFWwindow* window, int key, int scancode, int action, int mods)
{
     // Function is called first on GLFW_PRESS.

    if (action == GLFW_RELEASE) {
        switch (key) {
            case GLFW_KEY_C:
                rectangle_rot_status = !rectangle_rot_status;
                break;
            case GLFW_KEY_P:
                triangle_rot_status = !triangle_rot_status;
                break;
            case GLFW_KEY_UP:
                player.vx=0;
                break;
            case GLFW_KEY_DOWN:
                player.vx=0;
                break;
            case GLFW_KEY_LEFT:
                player.vz=0;
                break;
            case GLFW_KEY_RIGHT:
                player.vz=0;
                break;
            case GLFW_KEY_X:
                // do something ..
                break;
            default:
                break;
        }
    }
    else if (action == GLFW_PRESS) {
        switch (key) {
            case GLFW_KEY_ESCAPE:
                quit(window);
                break;
            case GLFW_KEY_UP:
                player.vx=-0.05;
                player.vz=0;
                break;
            case GLFW_KEY_DOWN:
                player.vx=0.05;
                player.vz=0;
                break;
            case GLFW_KEY_LEFT:
                player.vz=0.05;
                player.vx=0;
                break;
            case GLFW_KEY_RIGHT:
                player.vz=-0.05;
                player.vx=0;
                break;
            case GLFW_KEY_SPACE:
                if(player.vy<1)
                    player.vy+=0.3;
                break;
            case GLFW_KEY_V:
                camera.state ^= 1;
                break;
            

            default:
                break;
        }
    }
}
/* Executed when a mouse button is pressed/released */



/* Executed when window is resized to 'width' and 'height' */
/* Modify the bounds of the screen here in glm::ortho or Field of View in glm::Perspective */
void reshapeWindow (GLFWwindow* window, int width, int height)
{
    int fbwidth=width, fbheight=height;
    /* With Retina display on Mac OS X, GLFW's FramebufferSize
     is different from WindowSize */
    glfwGetFramebufferSize(window, &fbwidth, &fbheight);

	GLfloat fov = 90.0f;

	// sets the viewport of openGL renderer
	glViewport (0, 0, (GLsizei) fbwidth, (GLsizei) fbheight);

	// set the projection matrix as perspective
	/* glMatrixMode (GL_PROJECTION);
	   glLoadIdentity ();
	   gluPerspective (fov, (GLfloat) fbwidth / (GLfloat) fbheight, 0.1, 500.0); */
	// Store the projection matrix in a variable for future use
    // Perspective projection for 3D views
    // Matrices.projection = glm::perspective (fov, (GLfloat) fbwidth / (GLfloat) fbheight, 0.1f, 500.0f);

    // Ortho projection for 2D views
    Matrices.projection = glm::ortho(-4.0f, 4.0f, -4.0f, 4.0f, 0.1f, 500.0f);
}


void gravity(object *b)
{
    int val=b->vy;
    b->y+=b->vy;
    if(checkFloor(&player))
    {
        b->y-=val;
        b->y+=b->vy;
    }
    
    b->vy*=0.95;
    b->vy-=0.02;
    b->x+=b->vx;
    b->z+=b->vz;
            
}
bool checkFloor(object *b)
{
    bool flag =false;
    for(int i=0;i<flor.size();i++)
    {
        object f;
        f=flor[i];
        if(abs(b->x-f.x)<f.size+b->size)
        {
           // player.vx-=player.vx;
            if(abs(b->y-f.y)<f.size+b->size){
                    
                    if(abs(b->z-f.z)<f.size+b->size){
                      //  player.vz=-player.vz;
                        if(abs(player.vx)>0&&abs(player.y-f.y)<0.5)
                        {
                            player.x+=(abs(player.x-f.x)/(player.x-f.x))*0.05;
                            player.vx=0;
                        }
                        if(abs(player.vz)>0&&abs(player.y-f.y)<0.5)
                        {
                            player.z+=(abs(player.z-f.z)/(player.z-f.z))*0.05;
                            player.vz=0;
                        }
                        if(abs(player.vy)>0&&abs(player.y-f.y)<1)
                        {
                            if(player.vy)
                            player.y-=player.vy;
                            player.vy=0;
                        }
                    flag = true;
                    if(abs(flor[i].vy)!=0)
                    { 
                            player.vy=flor[i].vy;
                    }
                    if(abs(flor[i].vx)>0&&abs(player.vx)<0.01)
                            player.vx=flor[i].vx;
                    if(abs(flor[i].vz)>0&&abs(player.vz)<0.01)
                            player.vz=flor[i].vz;
                    }
        
                }
        }
    }
    return flag;
}
VAO* createCube(float s,int color)
{
    GLfloat  vertex_buffer_data[] = {

     -s,-s,-s, // triangle 1 : begin

     -s,-s, s,

     -s, s, s, // triangle 1 : end

     s, s,-s, // triangle 2 : begin

     -s,-s,-s,

     -s, s,-s, // triangle 2 : end

     s,-s, s,

     -s,-s,-s,

     s,-s,-s,

     s, s,-s,

     s,-s,-s,

     -s,-s,-s,

     -s,-s,-s,

     -s, s, s,

     -s, s,-s,

     s,-s, s,

     -s,-s, s,

     -s,-s,-s,

     -s, s, s,

     -s,-s, s,

     s,-s, s,

     s, s, s,

     s,-s,-s,

     s, s,-s,

     s,-s,-s,

     s, s, s,

     s,-s, s,

     s, s, s,

     s, s,-s,

     -s, s,-s,

     s, s, s,

     -s, s,-s,

     -s, s, s,

     s, s, s,

     -s, s, s,

     s,-s, s
     

 };
    static const GLfloat *color_buffer_data;
    if(color==0){
	static const GLfloat color_data[] = {

     0.583f,  0.771f,  0.014f,

     0.609f,  0.115f,  0.436f,

     0.327f,  0.483f,  0.844f,

     0.822f,  0.569f,  0.201f,

     0.435f,  0.602f,  0.223f,

     0.310f,  0.747f,  0.185f,

     0.597f,  0.770f,  0.761f,

     0.559f,  0.436f,  0.730f,

     0.359f,  0.583f,  0.152f,

     0.483f,  0.596f,  0.789f,

     0.559f,  0.861f,  0.639f,

     0.195f,  0.548f,  0.859f,

     0.014f,  0.184f,  0.576f,

     0.771f,  0.328f,  0.970f,

     0.406f,  0.615f,  0.116f,

     0.676f,  0.977f,  0.133f,

     0.971f,  0.572f,  0.833f,

     0.140f,  0.616f,  0.489f,

     0.997f,  0.513f,  0.064f,

     0.945f,  0.719f,  0.592f,

     0.543f,  0.021f,  0.978f,

     0.279f,  0.317f,  0.505f,

     0.167f,  0.620f,  0.077f,

     0.347f,  0.857f,  0.137f,

     0.055f,  0.953f,  0.042f,

     0.714f,  0.505f,  0.345f,

     0.783f,  0.290f,  0.734f,

     0.722f,  0.645f,  0.174f,

     0.302f,  0.455f,  0.848f,

     0.225f,  0.587f,  0.040f,

     0.517f,  0.713f,  0.338f,

     0.053f,  0.959f,  0.120f,

     0.393f,  0.621f,  0.362f,

     0.23f,  0.23f,  0.22f,

     0.820f,  0.883f,  0.371f,

     0.982f,  0.099f,  0.879f

    };
    color_buffer_data = color_data;
    }
    else if(color==1)
    {
    
	static const GLfloat color_data[] = {

     0.583f,  0.771f,  0.014f,

     0.609f,  0.115f,  0.436f,

     0.327f,  0.483f,  0.844f,

     0.822f,  0.569f,  0.201f,

     0.435f,  0.602f,  0.223f,

     0.310f,  0.747f,  0.185f,

     0.597f,  0.770f,  0.761f,

     0.559f,  0.436f,  0.730f,

     0.359f,  0.583f,  0.152f,

     0.483f,  0.596f,  0.789f,

     0.559f,  0.861f,  0.639f,

     0.195f,  0.548f,  0.859f,

     0.014f,  0.184f,  0.576f,

     0.771f,  0.328f,  0.970f,

     0.406f,  0.615f,  0.116f,
     
     0.23f,  0.23f,  0.23f,
     0.23f,  0.23f,  0.23f,
     0.23f,  0.23f,  0.23f,

     
     0.23f,  0.23f,  0.23f,
     0.23f,  0.23f,  0.23f,
     0.23f,  0.23f,  0.23f,
     
     0.55f,  0.53f,  0.51f,
     0.55f,  0.53f,  0.51f,
     0.55f,  0.53f,  0.51f,


     0.55f,  0.53f,  0.51f,
     0.55f,  0.53f,  0.51f,
     0.55f,  0.53f,  0.51f,
     
     0.0f, 0.81f, 0.82f,
     0.0f, 0.81f, 0.82f,
     0.0f, 0.81f, 0.82f,

     
     0.0f,  0.41f,  0.55f,
     0.0f,  0.41f,  0.55f,
     0.0f,  0.41f,  0.55f,
     

     
     0.23f,  0.23f,  0.23f,
     0.23f,  0.23f,  0.23f,
     0.23f,  0.23f,  0.23f,

    }; 
        color_buffer_data = color_data;
    }
   
    
    return create3DObject(GL_TRIANGLES, 36, vertex_buffer_data, color_buffer_data, GL_FILL);
}
void createObstacles()
{
    int obstacles[] = {29,69,46,86,7,13};
    for(int i=0;i<2;i++){
        flor[obstacles[i]].y=-1;
        slideBlock(&flor[obstacles[i]],0);
    } 
    
    for(int i=2;i<4;i++){
        flor[obstacles[i]].y=-1;
        slideBlock(&flor[obstacles[i]],1);
    }
    for(int i=4;i<6;i++)
    {
        flor[obstacles[i]].y=-1;
        slideBlock(&flor[obstacles[i]],3);
    }

}
void createFloor()
{
    for(int i=-5;i<5;i++)
            for(int j=-5;j<5;j++)
            {
                object box;
                box.posz=j;
                box.posx=i;
                box.posy=-2;
                box.x=i;
                box.y=-2;
                box.z=j;
                box.size=0.5;
                box.vx=0;
                box.vy=0;
                box.vz=0;
                box.sprite=createCube(0.5,1);
                flor.push_back(box);
            }
    deleteTiles();
    player.vy=0;
    player.vz=0;
    player.vx=0;
    player.x=0;
    player.y=0;
    player.z=0;
    player.size=0.2;
    player.on_platform=false;
    player.sprite=createCube(0.2,0);
}

float camera_rotation_angle = 90;
float rectangle_rotation = 0;
float triangle_rotation = 0;

void deleteTiles()
{
    int no_of_deletions = 6;
    int tiles_delete[]={14,22,79,43,63,80};
    for(int i=0;i<no_of_deletions;i++)
    {
       flor.erase(flor.begin()+tiles_delete[i]);
    }
}
void moveFloor()
{
    int no_of_moving = 4;
    int moving[]= {8,26,42,73};
    for(int i=0;i<no_of_moving;i++)
    {
        moveTile(&flor[moving[i]]);
        moveTile(&flor[moving[i]+9]);
    }
}
void slideBlock(object *tile,int dir)
{
    if(dir == 0)
    {
        cout<<"case 0\n";
        if(tile->vz==0)
                tile->vz=-0.025;
        tile->z+=tile->vz;
        if(tile->z<tile->posz||tile->z>5)
            tile->vz*=-1;

    }
    if(dir == 1)
    {
        cout<<"case 1\n";
        if(tile->vz==0)
                tile->vz=0.025;
        tile->z+=tile->vz;
        if(tile->z>tile->posz||tile->z<-5)
            tile->vz*=-1;

    }
    if(dir == 2)
    {
        cout<<"case 2\n";
        if(tile->vx==0)
                tile->vx=0.025;
        
        tile->x+=tile->vx;
        if(tile->x>tile->posx||tile->x<-5)
            tile->vx*=-1;

    }
    if(dir == 3)
    {
        cout<<"case 3\n";
        if(tile->vx==0)
                tile->vx=-0.025;
        tile->x+=tile->vx;
        if(tile->x<tile->posx||tile->x>5)
            tile->vx*=-1;

    }
}
void moveTile(object *tile)
{ 
    if(tile->vy==0)
    {
        int m=rand();
        if(m%2==0)
                tile->vy=0.005;
        else
                tile->vy=-0.005;
    }
    tile->y+=tile->vy;
    if((tile->y>Floor_limit+0.8)||(tile->y<Floor_limit-0.8))
            tile->vy*=-1;
}
/* Render the scene with openGL */
/* Edit this function according to your assignment */
void draw ()
{
  // clear the color and depth in the frame buffer
  glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

  // use the loaded shader program
  // Don't change unless you know what you are doing
  glUseProgram (programID);

  // Eye - Location of camera. Don't change unless you are sure!!
  glm::vec3 eye ( 5*cos(camera_rotation_angle*M_PI/180.0f), 0, 5*sin(camera_rotation_angle*M_PI/180.0f) );
  // Target - Where is the camera looking at.  Don't change unless you are sure!!
  glm::vec3 target (0, 0, 0);
  // Up - Up vector defines tilt of camera.  Don't change unless you are sure!!
  glm::vec3 up (0, 1, 0);

  // Compute Camera matrix (view)
  // Matrices.view = glm::lookAt( eye, target, up ); // Rotating Camera for 3D
  //  Don't change unless you are sure!!
  
  if(camera.state){
    camera.x=player.x+0.1;
    camera.y=player.y+3;
    camera.z=player.z+0.1;
  }
 else
 {
    camera.x=player.x+2;
    camera.y=player.y+2;
    camera.z=player.z+2;
 
 }  
  Matrices.view = glm::lookAt(glm::vec3(camera.x,camera.y,camera.z), glm::vec3(player.x,player.y,player.z), glm::vec3(0,1,0)); // Fixed camera for 2D (ortho) in XY plane

  // Compute ViewProject matrix as view/camera might not be changed for this frame (basic scenario)
  //  Don't change unless you are sure!!
  glm::mat4 VP = Matrices.projection * Matrices.view;

  // Send our transformation to the currently bound shader, in the "MVP" uniform
  // For each model you render, since the MVP will be different (at least the M part)
  //  Don't change unless you are sure!!
  glm::mat4 MVP;	// MVP = Projection * View * Model

  // Load identity to model matrix

  /* Render your scene */
    moveFloor();
    createObstacles();
    for(int i=0;i<flor.size();i++)
    {
        Matrices.model = glm::mat4(1.0f);
        object box=flor[i];
        glm::mat4 translateTile = glm::translate (glm::vec3(box.x, box.y, box.z)); // glTranslatef

        glm::mat4 floorTransform = translateTile;
        Matrices.model *= floorTransform; 
        MVP = VP * Matrices.model; // MVP = p * V * M

        glUniformMatrix4fv(Matrices.MatrixID, 1, GL_FALSE, &MVP[0][0]);
        draw3DObject(box.sprite); 
    }
  // draw3DObject draws the VAO given to it using current MVP matrix
  //draw3DObject(triangle);
  //draw3DObject(player.sprite);
  // Pop matrix to undo transformations till last push matrix instead of recomputing model matrix
  // glPopMatrix ();

  /*glm::mat4 translateRectangle = glm::translate (glm::vec3(2, 0, 0));        // glTranslatef
  glm::mat4 rotateRectangle = glm::rotate((float)(rectangle_rotation*M_PI/180.0f), glm::vec3(0,0,1)); // rotate about vector (-1,1,1)
  */
  Matrices.model = glm::mat4(1.0f);
  glm::mat4 translatePlayer = glm::translate (glm::vec3(player.x, player.y, player.z)); // glTranslatef
  Matrices.model *= translatePlayer;
  MVP = VP * Matrices.model;
  glUniformMatrix4fv(Matrices.MatrixID, 1, GL_FALSE, &MVP[0][0]);
  draw3DObject(player.sprite);
  gravity(&player);
  // draw3DObject draws the VAO given to it using current MVP matrix

  // Increment angles
  float increments = 1;

  //camera_rotation_angle++; // Simulating camera rotation
  triangle_rotation = triangle_rotation + increments*triangle_rot_dir*triangle_rot_status;
  rectangle_rotation = rectangle_rotation + increments*rectangle_rot_dir*rectangle_rot_status;
}

/* Initialise glfw window, I/O callbacks and the renderer to use */
/* Nothing to Edit here */
GLFWwindow* initGLFW (int width, int height)
{
    GLFWwindow* window; // window desciptor/handle

    glfwSetErrorCallback(error_callback);
    if (!glfwInit()) {
        exit(EXIT_FAILURE);
    }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    window = glfwCreateWindow(width, height, "Sample OpenGL 3.3 Application", NULL, NULL);

    if (!window) {
        glfwTerminate();
        exit(EXIT_FAILURE);
    }

    glfwMakeContextCurrent(window);
    gladLoadGLLoader((GLADloadproc) glfwGetProcAddress);
    glfwSwapInterval( 1 );

    /* --- register callbacks with GLFW --- */

    /* Register function to handle window resizes */
    /* With Retina display on Mac OS X GLFW's FramebufferSize
     is different from WindowSize */
    glfwSetFramebufferSizeCallback(window, reshapeWindow);
    glfwSetWindowSizeCallback(window, reshapeWindow);

    /* Register function to handle window close */
    glfwSetWindowCloseCallback(window, quit);

    /* Register function to handle keyboard input */
    glfwSetKeyCallback(window, keyboard);      // general keyboard input
    glfwSetCharCallback(window, keyboardChar);  // simpler specific character handling

    /* Register function to handle mouse click */
    glfwSetMouseButtonCallback(window, mouseButton);  // mouse button clicks

    return window;
}

/* Initialize the OpenGL rendering properties */
/* Add all the models to be created here */
void initGL (GLFWwindow* window, int width, int height)
{
    /* Objects should be created before any other gl function and shaders */
	// Create the models
	//createTriangle (); // Generate the VAO, VBOs, vertices data & copy into the array buffer
	//createRectangle ();
	camera.state=0;
    createFloor();
    // Create and compile our GLSL program from the shaders
	programID = LoadShaders( "Sample_GL.vert", "Sample_GL.frag" );
	// Get a handle for our "MVP" uniform
	Matrices.MatrixID = glGetUniformLocation(programID, "MVP");

	
	reshapeWindow (window, width, height);

    // Background color of the scene
	glClearColor (0.3f, 0.3f, 0.3f, 0.0f); // R, G, B, A
	glClearDepth (1.0f);

	glEnable (GL_DEPTH_TEST);
	glDepthFunc (GL_LEQUAL);

    cout << "VENDOR: " << glGetString(GL_VENDOR) << endl;
    cout << "RENDERER: " << glGetString(GL_RENDERER) << endl;
    cout << "VERSION: " << glGetString(GL_VERSION) << endl;
    cout << "GLSL: " << glGetString(GL_SHADING_LANGUAGE_VERSION) << endl;
}

int main (int argc, char** argv)
{	int width = 1000;
	int height = 1000;

    GLFWwindow* window = initGLFW(width, height);

	initGL (window, width, height);

    double last_update_time = glfwGetTime(), current_time;

    /* Draw in loop */
    while (!glfwWindowShouldClose(window)) {

        // OpenGL Draw commands
        draw();

        // Swap Frame Buffer in double buffering
        glfwSwapBuffers(window);

        // Poll for Keyboard and mouse events
        glfwPollEvents();

        // Control based on time (Time based transformation like 5 degrees rotation every 0.5s)
        current_time = glfwGetTime(); // Time in seconds
        if ((current_time - last_update_time) >= 0.5) { // atleast 0.5s elapsed since last frame
            // do something every 0.5 seconds ..
            last_update_time = current_time;
        }
    }

    glfwTerminate();
    exit(EXIT_SUCCESS);
}
