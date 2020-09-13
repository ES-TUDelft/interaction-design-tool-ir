# Design Guidelines
## For a successful Human-Robot Interaction 

* **Split** the interaction into different sections (e.g., opening and closing) and multiple parts (e.g., monologues and questions) to create a smooth flow when the robot is executing the blocks;

* Make each **interaction block** complete and self-contained: 
  * Always define the block message (i.e., if left blank, the block is useless);
  * It is advisable to benefit from the robot tablet (if any) for providing visual and fallback support;
  * Replace repetitive blocks with loops to simplify the overall design;

* Make each **monologue** clear, concise and precise: 
  * not too long so that people can follow; 
  * not too short to be meaningless;
  * divided into parts or sections (e.g., greeting, presenting-self, farewell)

* Design a **question** to be only a “question”: 
    * Avoid mixing monologues & questions in one block;
    * A complex robot message (i.e., a long or mixed question) is ambiguous, unclear and not easy to answer;
    * When you want to provide an introduction (e.g., explanation) for a question, create two (or more) blocks, i.e., one block to introduce the question and one block to clearly ask the actual question and wait for user answers;
    * Define both **user answers** and **robot feedbacks** (e.g., a user answer with no feedback may leave the user unsure if his/her answer was recorded by the robot, which will affect the interaction flow and clarity); 
    * Make user answers short with multiple options (e.g., yes, sure, of course)
    * **Note:** the confirmation block is a specific case of questions with yes/no answers; 

* Split the **instructions** (e.g., when explaining an activity) into steps so that the robot proceeds with the following sequence of actions: 
    * a) explain one step or more, depending on the audience (e.g., elderly versus youth) and the task complexity;
    * b) ask the user(s) if it’s clear;
    * c) continue with the next steps if all is clear, or repeat (a) otherwise;
