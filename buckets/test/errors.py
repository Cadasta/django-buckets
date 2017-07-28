EXCEED_MAX_SIZE = """
    <Error>
        <Code>EntityTooLarge</Code>
        <Message>Your proposed upload exceeds the maximum
                 allowed size</Message>
        <MaxSizeAllowed>{max_size}</MaxSizeAllowed>
        <ProposedSize>{proposed_size}</ProposedSize>
    </Error>
"""
