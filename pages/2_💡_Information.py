import streamlit as st

st.title("Chat Bot Information")

st.markdown(
    """
    This chat bot is designed to assist users with questions related to Amazon EC2 (Elastic Compute Cloud). This Retrieval-Augmented Generation (RAG) system uses the next AWS public technical documents:
    * [Amazon EC2 User Guide](https://docs.aws.amazon.com/pdfs/AWSEC2/latest/UserGuide/ec2-ug.pdf)
    * [Amazon EC2 Developer Guide](https://docs.aws.amazon.com/pdfs/ec2/latest/devguide/ec2-dg.pdf).\n
    Here are some considerations you should keep in mind about this project:
    - This chatbot does not remember previous questions or answers. Always verify the information received from the chatbot.
    - The system has showed a average performance in robustness tests, with questions such as "my server keeps restarting by itself, how do i stop that??".
    """
)